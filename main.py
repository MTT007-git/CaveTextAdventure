import time
import re
import random
import winsound
import anim
from quest_SPOILERS import quest, ignore_re


def sound(s: str) -> None:
    """
    Play a sound. If you are not on Windows, this is the perfect place to change the function
    :param s: path to sound file (wav)
    :return: None
    """
    winsound.PlaySound(s, winsound.SND_ASYNC)


inventory: set[str] = set()


def showroom(room: str, prevroomid: str) -> str:
    """
    Show a room
    :param room: room id to show
    :param prevroomid: previous room id
    :return: next room id
    """
    if not handlemissing(room):
        return "start", prevroomid
    if quest[room]["image"] != "":
        image: str = quest[room]["image"]
        anim_ended = False
    else:
        image: str = ""
        anim_ended = True
    frame: int = 0
    if quest[room]["sound"] != "":
        sound(quest[room]["sound"])
    if image != "" and not anim_ended:
        im, anim_ended = anim.getanim(image, frame)
        print("\n".join(im)+"\n", end="")
    parts: list[str] = quest[room]["text"].split("&")
    for i in range(len(parts)):
        if i % 2 == 1:
            if parts[i][0].lower() == "s":  # play sound
                sound(parts[i][1:])
            elif parts[i][0].lower() == "t":  # wait
                t = time.time()
                while time.time() - t < float(parts[i][1:]):
                    if image != "" and not anim_ended:
                        im, anim_ended = anim.getanim(image, frame)
                        pr = []
                        for j in range(i):
                            if j % 2 == 0:
                                pr.append(parts[j])
                        print("\n".join(im)+"\n"+"".join(pr), end="")
                        frame += 1
                        time.sleep(0.1)
            elif parts[i][0].lower() == "i":  # show image
                image = parts[i][1:]
                anim_ended = False
                frame = 0
                if image != "" and not anim_ended:
                    im, anim_ended = anim.getanim(image, frame)
                else:
                    im = []
                pr = []
                for j in range(i):
                    if j % 2 == 0:
                        pr.append(parts[j])
                print("\n".join(im)+"\n"+"".join(pr), end="")
                frame += 1
                time.sleep(0.1)
            elif parts[i][0].lower() == "w":  # wait for animation to end
                while not anim_ended:
                    im, anim_ended = anim.getanim(image, frame)
                    pr = []
                    for j in range(i):
                        if j % 2 == 0:
                            pr.append(parts[j])
                    print("\n".join(im)+"\n"+"".join(pr), end="")
                    frame += 1
                    time.sleep(0.1)
            elif parts[i][0].lower() == "r":  # Generate new random value in random inventory
                if random.randint(0, 1) == 1:
                    inventory.add("random")
                elif "random" in inventory:
                    inventory.remove("random")
            elif parts[i][0] == "+":  # add item to inventory
                inventory.add(parts[i][1:])
            elif parts[i][0] == "-":  # delete item from inventory
                if parts[i][1:] in inventory:
                    inventory.remove(parts[i][1:])
            elif parts[i][0] in ("=", "!"):  # print the text in triangular brackets<> only if item exists / doesn't
                if (parts[i][1:] in inventory and parts[i][0] == "=") or (parts[i][1:] not in inventory and
                                                                          parts[i][0] == "!"):
                    if ">" in parts[i + 1]:
                        idx: int = parts[i + 1].index(">")
                        parts[i + 1] = parts[i + 1][1:idx] + parts[i + 1][idx + 1:]
                    else:
                        parts[i + 1] = parts[i + 1][1:]
                        brackets: int = 1
                        b: bool = False
                        for j in range(i + 1, len(parts)):
                            if j % 2 == 0:
                                for k in range(len(parts[j])):
                                    if "<" == parts[j][k]:
                                        brackets += 1
                                    if ">" == parts[j][k]:
                                        brackets -= 1
                                        if brackets == 0:
                                            parts[j] = parts[j][:k] + parts[j][k + 1:]
                                            b = True
                                            break
                                if b:
                                    break
                else:
                    if ">" in parts[i + 1]:
                        parts[i + 1] = parts[i + 1][parts[i + 1].index(">") + 1:]
                    else:
                        parts[i + 1] = ""
                        brackets = 1
                        b: bool = False
                        for j in range(i + 1, len(parts)):
                            if j % 2 == 0:
                                for k in range(len(parts[j])):
                                    if "<" == parts[j][k]:
                                        brackets += 1
                                    if ">" == parts[j][k]:
                                        brackets -= 1
                                        if brackets == 0:
                                            parts[j] = parts[j][k + 1:]
                                            b = True
                                            break
                                if b:
                                    break
                                parts[j] = ""
                            else:
                                parts[j] = "#"
        else:
            print(parts[i], end="")
    print("\n", end="")
    while not anim_ended:
        im, anim_ended = anim.getanim(image, frame)
        pr = []
        for i in range(len(parts)):
            if i % 2 == 0:
                pr.append(parts[i])
        print("\n".join(im) + "\n" + "".join(pr)+"\n", end="")
        frame += 1
        time.sleep(0.1)
    options: dict[str: str] = getoptions(room)
    chosen: str = re.sub(ignore_re, "", input()).strip()
    while chosen not in options:
        print("Sorry, I didn't understand.\n", end="")
        chosen: str = re.sub(ignore_re, "", input()).strip()
    if options[chosen] == "return":
        options = getoptions(prevroomid)
        chosen: str = re.sub(ignore_re, "", input()).strip()
        while chosen not in options:
            print("Sorry, I didn't understand.\n", end="")
            chosen: str = re.sub(ignore_re, "", input()).strip()
        return options[chosen], prevroomid
    return options[chosen], room


def handlemissing(room: str) -> bool:
    """
    Handle missing parametrs
    :param room: room id
    :return: should the program continue
    """
    if room not in quest:
        print(f"The room \"{room}\" doesn't exist. Sending back to start.")
        return False
    if "text" not in quest[room]:
        quest[room]["text"] = ""
    if "options" not in quest[room]:
        quest[room]["options"] = [(f"The room \"{room}\" doesn't have any options. Go to start.", "s", "start")]
    if "hiddenoptions" not in quest[room]:
        quest[room]["hiddenoptions"] = {}
    if "image" not in quest[room]:
        quest[room]["image"] = ""
    if "sound" not in quest[room]:
        quest[room]["sound"] = ""
    return True


def getoptions(room: str) -> dict[str: str]:
    """
    Gets the options for a room
    :param room: room id
    :return: options
    """
    options: dict[tuple[str, ...]: str] = {}
    for i, j in quest[room]["hiddenoptions"].items():
        if isinstance(i, str):
            options[i] = j
        else:
            for k in i:
                options[k] = j
    toprint: list[str] = []
    for i in range(len(quest[room]["options"])):
        if isinstance(quest[room]["options"][i][1], str):
            quest[room]["options"][i] = (quest[room]["options"][i][0], (quest[room]["options"][i][1],)
                                         ) + quest[room]["options"][i][2:]
        if len(quest[room]["options"][i]) > 3:
            for j in range(3, len(quest[room]["options"][i])):
                if (quest[room]["options"][i][j][0] == "=" and quest[room]["options"][i][j][1:] not in inventory) or (
                        quest[room]["options"][i][j][0] == "!" and quest[room]["options"][i][j][1:] in inventory):
                    break
            else:
                for j in quest[room]["options"][i][1]:
                    options[j] = quest[room]["options"][i][2]
                toprint.append(f"{quest[room]['options'][i][1][0]}: {quest[room]['options'][i][0]}")
        else:
            for j in quest[room]["options"][i][1]:
                options[j] = quest[room]["options"][i][2]
            toprint.append(f"{quest[room]['options'][i][1][0]}: {quest[room]['options'][i][0]}")
    print("\n".join(toprint)+"\n", end="")
    return options


nextroom: str
prevroom: str
nextroom, prevroom = showroom("start", "start")
while nextroom != "end":
    nextroom, prevroom = showroom(nextroom, prevroom)

