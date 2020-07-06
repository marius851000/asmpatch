def parse_map(map_content):
    is_inside_section = False
    objects = {}
    lenght = 0
    for line in map_content.split("\n"):
        if line == "":
            if is_inside_section:
                lenght += int(section_len, 16)
                is_inside_section = False
            continue

        splited = []
        actual_string = ""
        line += " "
        for chara in line:
            if chara in [" ", "\t"]:
                if actual_string != "":
                    splited.append(actual_string)
                    actual_string = ""
            else:
                actual_string += chara

        if splited[0] == "*fill*":
            continue

        if line[0] == ".": # section start
            section_name = splited[0]
            section_len = splited[2]
            is_inside_section = True
            continue

        if is_inside_section:
            if line[1] == ".":
                continue
            else:
                objects[splited[1]] = splited[0]
    return {
        "lenght": lenght,
        "offsets": objects
    }
