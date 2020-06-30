def parse_asm(content):
    result = []
    for line in content.split("\n"):
        # clean the line
        if line == "":
            continue
        # separate the operand and comment
        operands = []
        string_symbol = None #the symbol to close the string
        actual_string = ""
        last_was_escape = False #true if the last character was a \ in a string
        operand_start = True
        actual_operand = ""
        comment = ""
        inside_comment = False
        for chara in line:
            if inside_comment:
                comment += chara
            elif string_symbol != None:
                if last_was_escape:
                    actual_string += "\\"+chara
                    last_was_escape = False
                elif chara == "\\":
                    last_was_escape = True
                elif chara == string_symbol:
                    operands.append(string_symbol + actual_string + string_symbol)
                    string_symbol = None
                else:
                    actual_string += chara
            elif chara == ";":
                if actual_operand != "":
                    operands.append(actual_operand)
                    actual_operand = ""
                inside_comment = True
            elif chara == " " or chara == "\t":
                if actual_operand != "":
                    operands.append(actual_operand)
                    actual_operand = ""
                operand_start = True
            elif chara == "\"" or chara == "'":
                string_symbol = chara
                actual_string = ""
                last_was_escape = False
            else:
                actual_operand += chara
        if actual_operand != "":
            operands.append(actual_operand)
            actual_operand = ""
        # create the result
        line_result = {"comment": comment}
        if len(operands) == 0:
            if comment == "":
                continue
            else:
                line_result["category"] = "comment"
        else:
            if operands[0][0] == ".":
                line_result["category"] = "command"
                line_result["name"] = operands[0]
                if len(operands) == 1:
                    line_result["parameter"] = []
                else:
                    line_result["parameter"] = operands[1:]
            elif operands[0][-1] == ":":
                line_result["category"] = "definition"
                line_result["name"] = operands[0][0:-1]
                if len(operands) != 1:
                    print("WARNING: the definition of {} contain more than one parameter".format(line_result["name"]))
            else:
                line_result["category"] = "assembly"
                line_result["opcode"] = operands[0]
                if len(operands) == 1:
                    line_result["parameter"] = []
                else:
                    line_result["parameter"] = operands[1:]
        result.append(line_result)
    return result

def recreate_asm_line(parsed, with_comment=True):
    category = parsed["category"]

    if category == "command":
        line = parsed["name"]
    elif category == "assembly":
        line = parsed["opcode"]
    elif category == "definition":
        line = parsed["name"]+":"
    else:
        line = ""

    if category in ["command", "assembly"]:
        if len(parsed["parameter"]) != 0:
            for param in parsed["parameter"]:
                line += " " + param

    if with_comment:
        if parsed["comment"] != "":
            if category == "comment":
                line += ";"
            else:
                line += " ;"
            line += parsed["comment"]

    return line

def recreate_asm(parsed, with_comment=True):
    result = ""
    for parsed_line in parsed:
        result += recreate_asm_line(parsed_line, with_comment) + "\n"
    return result
