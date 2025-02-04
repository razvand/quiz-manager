import json
import re

def get_meta(question_dict : dict, key : str):
    if(not (key in question_dict["metadata"])):
        return ""
    if(len(question_dict["metadata"][key]) == 1):
        return question_dict["metadata"][key][0]
    else:
        return question_dict["metadata"][key]

def quiz_hr_to_json(file_content : str):
    question_arr = file_content.split("\n\n")
    question_arr_json = list(map(hr_to_json, question_arr))
    return question_arr_json

def quiz_json_to_hr(json_arr : list):
    return list(map(json_to_hr, json_arr))

def json_to_hr(json_obj: str) -> str:
    """
    Generates a question in HR format from JSON string
    :param json_obj: a question stored in JSON format
    :return: a string representing a question in HR format 
    """
    json_q = json.loads(json_obj)
    # Adding Tagline
    hr = ""

    for tag in json_q["metadata"]:
        hr += tag + ":"
        for item in json_q["metadata"][tag]:
            hr += item + ","
        hr = hr[:-1] + ";"
    hr += "\n"

    # Adding Statement
    hr += json_q["statement"]

    # Adding Answers
    for answer in json_q["answers"]:
        stmt = answer["statement"]
        correct = "+" if answer["correct"] else "-"
        hr += correct + " " + stmt
    return hr

def hr_to_json(hr: str) -> str:
    """
    Generates a JSON string for the given HR question
    :param hr: a string representing a question in HR format
    :return: string representing a question in JSON format
    """

    # Copy object to prevent side effects in caller
    hr_copy = str(hr).rstrip()

    # Template question to be completed with necessary info and returned
    question = {
        "statement": "",
        "metadata": {},
        "answers": [
            # {
            #     "statement": "",
            #     "correct": False,
            #     "grade": 0.0
            # }
        ],
        "correct_answers_no": 0
    }

    # Assign tags
    partition = hr_copy.partition("\n")
    for tag in partition[0].split(";"):
        splitTags = tag.split(":")
        if(len(splitTags) < 2):
            break
        key = splitTags[0]
        value = splitTags[1]

        # If the key has been declared in template
        if(key in question.keys()):
            question[key] = value
        else:
            question["metadata"][key] = value.split(",")

    # Get question statement
    # Find where the answer section starts
    answers_index = min(partition[2].find("+"), partition[2].find("-"))
    statement = partition[2][:answers_index]
    question["statement"] = statement

    # Assign Answers
    answer_list = re.split(r"\n", partition[2][answers_index:])
    # Get number of correct answers to compute grade awarded for each
    # correct answer
    question["correct_answers_no"] = len(
        [ans for ans in answer_list if ans[0] == "+"])

    # Preliminary pass through answer list to concatenate multiline answers
    for i in range(1, len(answer_list)):
        if answer_list[i][0] != "+" and answer_list[i][0] != "-":
            answer_list[i - 1] += "\n" + answer_list[i]
            continue

    # Remove continuations of multiline answers from list
    answer_list = [answer for answer in answer_list if not (
        answer[0] != "+" and answer[0] != "-")]

    grade = 1 / (question["correct_answers_no"] * 1.0)
    # Add answers to answer list in JSON object
    for answer in answer_list:
        if(answer[0] == "+"):
            question["answers"].append(
                {
                    "statement": answer[2:] + "\n",
                    "correct": True,
                    "grade": grade
                }
            )
        elif(answer[0] == "-"):
            question["answers"].append(
                {
                    "statement": answer[2:] + "\n",
                    "correct": False,
                    "grade": -0.5
                }
            )

    return json.dumps(question, indent=4)
