"""
Quest dict format:
"room_id": {}  # dictionary values:

"text": "room &anything& text"  # &anything& means:
"&s{soundfile_wav}&"  # play sound
"&t{seconds}&"        # wait
"&i{image_path}&"     # show image
"&w{ignored}&"        # wait for animation to end
"&r{ignored}&"        # Generate new random value in random inventory (check with =random)
"&+{item_name}&"      # add item to inventory
"&-{item_name}&"      # delete item from inventory (if item exists)
"&={item_name}&<t>"   # print the text in triangular brackets<> only if item exists
"&!{item_name}&<t>"   # print the text in triangular brackets<> only if item doesn't exist
"&#{comment}&"        # comment (use any unused starting symbol)

"options": [("option name", "option_shortcut", "option_room", "option_conition"), ...]  # optinons from which to choose
# option_condition: =item_name or !item_name, may not be present
# special option_room: return, start, end

"hiddenoptions": {"option_shortcut": "option_room"}  # same as "options", but not shown

"image": "image_path"  # image to show, same as "&i{image_path}&other text" in "text"

"sound": "soundfile_wav"  # sound to play, same as "&s{soundfile_wav}&other text" in "text"


SPOILERS AHEAD









Images - Sora (ChatGPT) + image_to_ascii.py
Audio - freepik.com and minimax.io for speech
Video - hailuoai.video + image_to_ascii.py
"""

ignore_re = r"\bgo\b|\bto\b|\bthe\b|\btry\b|\buse\b"

boss_lose_health = "&=boss_1&<&-boss_1&&+boss_0&>&=boss_2&<&-boss_2&&+boss_1&>&=boss_3&<&-boss_3&&+boss_2&>" \
                   "&=boss_4&<&-boss_4&&+boss_3&>&=boss_5&<&-boss_5&&+boss_4&>&=boss_6&<&-boss_6&&+boss_5&>" \
                   "&=boss_7&<&-boss_7&&+boss_6&>&=boss_8&<&-boss_8&&+boss_7&>&=boss_9&<&-boss_9&&+boss_8&>" \
                   "&=boss_10&<&-boss_10&&+boss_9&>"

player_lose_health = "&=player_1&<&-player_1&&+player_0&&+death&>&=player_2&<&-player_2&&+player_1&>" \
                     "&=player_3&<&-player_3&&+player_2&>&=player_4&<&-player_4&&+player_3&>" \
                     "&=player_5&<&-player_5&&+player_4&>&=player_6&<&-player_6&&+player_5&>" \
                     "&=player_7&<&-player_7&&+player_6&>&=player_8&<&-player_8&&+player_7&>" \
                     "&=player_9&<&-player_9&&+player_8&>&=player_10&<&-player_10&&+player_9&>"

hidden = {("inv", "inventory", "open inventory", "open inv"): "inventory"}

quest: dict[str: dict[str: str | list[tuple[str, str | tuple[str, ...], str] | tuple[
    str, str | tuple[str, ...], str, str]] | dict[str | tuple[str, ...]: str]]] = {
    "inventory": {"text": "Your inventory:&=door_key&<\nKey>&=letter&<\nLetter>&=shiny_sword&<\nShining sword>"
                          "&=sword&<\nSword>\nYour HP: &=player_10&<10>&=player_9&<9>&=player_8&<8>&=player_7&<7>"
                          "&=player_6&<6>&=player_5&<5>&=player_4&<4>&=player_3&<3>&=player_2&<2>&=player_1&<1>"
                          "&=player_0&<0>.&=boss&<\nEgg HP: &=boss_10&<10>&=boss_9&<9>&=boss_8&<8>&=boss_7&<7>"
                          "&=boss_6&<6>&=boss_5&<5>&=boss_4&<4>&=boss_3&<3>&=boss_2&<2>&=boss_1&<1>&=boss_0&<0>.>",
                  "options": [("Return", ("return", ""), "return")], "hiddenoptions": hidden},
    "start": {"text": "&+player_10&Use \"inv\" to open your inventory and see your stats.\n"
                      "You enter a big cave.\n&t2&Something glows inside...\n&t2&&idead_end.ascii&"
                      "&sentrance.wav&The entrance behind you closes\n&t2&The glowing stops.\n&t1&"
                      "You can't see anything.", "image": "cave_entrance.ascii",
              "options": [("Walk forward", ("walk", "w", "forward"), "dead_end"),
                          ("Wait", "wait", "look_at_door")], "hiddenoptions": hidden},
    "look_at_door": {
        "text": "You wait for your eyes to see the inside of the cave.\n&t1&You look at the place where there "
                "was an entrance.\n&t1&&icave_door.ascii&Instead of the it, you see a giant wooden door.",
        "image": "dead_end.ascii", "options": [("Go through the door", ("door", "d"), "try_door"),
                                               ("Turn around", ("turn", "turn around"), "dead_end")],
        "hiddenoptions": hidden},
    "dead_end": {"text": "You see a dead end.", "image": "dead_end.ascii",
                 "options": [("Return", ("return", "r", ""), "return")], "hiddenoptions": hidden},
    "try_door": {"text": "You try to go through the door, but it doen't move.", "image": "cave_door.ascii",
                 "options": [("Look for a key", ("look", "key"), "look_for_door_key"),
                             ("Kick the door", "kick", "kick_door")], "hiddenoptions": hidden},
    "look_for_door_key": {"text": "&r&&=random&<&ikey.ascii&&spickup.wav&You found the key!&+door_key&&+fair_door&>"
                                  "&!random&<You didn't find the key.>", "image": "dead_end.ascii",
                          "options": [("Look more carefully", ("look", "more"), "look_for_door_key", "!random"),
                                      ("Go kick the door", ("kick", "kick door"), "kick_door", "!random"),
                                      ("Open the door", ("open", "open door"), "open_door", "=random"),
                                      ("Look for something else", "look", "look_more", "=random")],
                          "hiddenoptions": hidden},
    "look_more": {"text": "&+letter&&spickup.wav&You found a letter:\n\n&t1&To: Dan\nFrom: Kevin\n\n"
                          "Come to me right now.\nThere is an intruder!", "image": "dead_end.ascii",
                  "options": [("Take it and open the door", ("open", "open door", "take", "take it", ""),
                               "open_door")], "hiddenoptions": hidden},
    "kick_door": {"text": "You kick the door.\n&t1&&r&&=random&<The lock breaks.>"
                          "&!random&<It budges a little, but you couldn't open it.>", "image": "cave_door.ascii",
                  "sound": "door_kick.wav", "options": [("Kick it again", ("kick", "again"), "kick_door", "!random"),
                                                        ("Look for a key", ("look", "key"), "look_for_door_key",
                                                         "!random"), ("Open the door", ("open", "open door", ""),
                                                                      "open_door", "=random")],
                  "hiddenoptions": hidden},
    "open_door": {"text": "When you push on the door, a mesmorising sight opens up.\n&t1&&sdoor_open.wav&&t6&"
                          "&iopen_door.ascii&The sun shines through the ceiling, blinding you.\n&t2&"
                          "In the room, you see a table with a glowing orb.\n&t2&"
                          "The orb lures you towards itself.\n&t1&"
                          "Behind the table, there is a old chest.",
                  "image": "opening_door.ascii",
                  "options": [("Go towards the glowing orb", ("orb", "glowing orb"), "glowing_orb"),
                              ("Try the door key on the chest", ("key", "door", "door key"), "key_chest", "=door_key"),
                              ("Look for a chest key", ("look", "chest key"), "look_for_chest_key"),
                              ("Open the chest by force", ("open", "force"), "open_chest_force")],
                  "hiddenoptions": hidden},
    "glowing_orb": {"text": "&+orb_curse&You walk towards the glowing orb.\n&t1&"
                            "You can't stop going towards it.\n&t1&&w&You touch it.\n"
                            f"&t2&{player_lose_health}You lose 1 HP.\n&t2&"
                            "You start hearing voices.\n&t2&&sorb_talk.wav& - Someone's here...\n&t2&"
                            " - Are you sure?\n&t2& - My trap got set off...\n&t2.5& - Maybe someone forgot?\n&t3&"
                            " - No, I'm sure...\n&t3& - Let's prepare then!"
                            "&!tunnel_notice&<&+tunnel_notice&\n\n&t1&"
                            "Also, you notice a small tunnel on the left side of the room.>",
                    "image": "glowing_orb.ascii",
                    "options": [("Try the door key on the chest", ("key", "door", "door key"), "key_chest",
                                 "=door_key"), ("Look for a chest key", ("look", "chest key"), "look_for_chest_key",
                                                "!looked_for_chest_key"),
                                ("Open the chest by force", ("open", "force"), "open_chest_force"),
                                ("Ignore the chest, go through the tunnel", ("tunnel", "ignore"), "tunnel")],
                    "hiddenoptions": hidden},
    "key_chest": {"text": "&-door_key&You try the door key on the chest.\n&t1"
                          "&It gets stuck, but the chest doesn't open.&!tunnel_notice&<&t1&&+tunnel_notice&\n"
                          "You also notice a small tunnel on the left side of the room.>", "image": "chest.ascii",
                  "options": [("Go towards the glowing orb", ("orb", "glowing orb"), "glowing_orb", "!orb_curse"),
                              ("Look for a chest key", ("look", "key", "chest key"), "look_for_chest_key",
                               "!looked_for_chest_key"), ("Open the chest by force", ("open", "force"),
                                                          "open_chest_force"),
                              ("Ignore the chest, go through the tunnel", ("tunnel", "ignore"), "tunnel")],
                  "hiddenoptions": hidden},
    "look_for_chest_key": {"text": "&+looked_for_chest_key&You try to find a key for the chest, but to no avail."
                                   "&!tunnel_notice&<&t1&&+tunnel_notice&\n"
                                   "You also notice a small tunnel on the left side of the room.>",
                           "image": "chest.ascii",
                           "options": [("Go towards the glowing orb", ("orb", "glowing orb"), "glowing_orb",
                                        "!orb_curse"), ("Try the door key on the chest", ("key", "door", "door key"),
                                                        "key_chest", "=door_key"),
                                       ("Open the chest by force", ("open", "force"), "open_chest_force"),
                                       ("Ignore the chest, go through the tunnel", ("tunnel", "ignore"), "tunnel")],
                           "hiddenoptions": hidden},
    "open_chest_force": {"text": "&+mimic_4&You open the chest easily, but it turns out to be a mimic.\n&t1&"
                                 "&schest_kick.wav&You jump away, having no weapon to fight it but your bare hands."
                                 "&!tunnel_notice&<&+tunnel_notice&\n"
                                 "You notice a small tunnel on the left side of the room.>",
                         "image": "mimic_open.ascii",
                         "options": [("Flee to the tunnel", ("tunnel", "flee"), "tunnel"),
                                     ("Punch the mimic", "punch", "punch_mimic"),
                                     ("Kick the mimic", "kick", "kick_mimic")], "hiddenoptions": hidden},
    "punch_mimic": {"text": "&=mimic_1&<&-mimic_1&&+shiny_sword&You punch the mimic, and it dies.\n&t1&"
                            "&ishiny_sword.ascii&The chest opens to reveal a shining sword.\n&t1&&spickup.wav&"
                            "You take it.>&=mimic_2&<&-mimic_2&&+mimic_1&>&=mimic_3&<&-mimic_3&&+mimic_2&>"
                            "&=mimic_4&<&-mimic_4&&+mimic_3&>&!shiny_sword&<"
                            "&=mimic_punch&<&+death&You punch it again, but it knows your tricks.\n&t1&"
                            "It bites your hand and it starts bleeding.\n&t2&Badly.\n&t2&&ideath.ascii&You die.>"
                            "&!mimic_punch&<&-mimic_kick&&+mimic_punch&You punch the mimic, but it fights back.\n&t1&"
                            "&r&&=random&<&r&&=random&<You barely survive.>"
                            f"&!random&<{player_lose_health}You lose 1 HP.>&+random&>"
                            f"&!random&<{player_lose_health}You lose 1 HP.>>>", "image": "mimic.ascii",
                    "sound": "chest_kick.wav",
                    "options": [("The end", "", "ending", "=death"),
                                ("Punch the mimic", "punch", "punch_mimic", "!death", "!shiny_sword"),
                                ("Kick the mimic", "kick", "kick_mimic", "!death", "!shiny_sword"),
                                ("Go through the tunnel", ("tunnel", ""), "tunnel", "=shiny_sword")],
                    "hiddenoptions": hidden},
    "kick_mimic": {"text": "&=mimic_1&<&-mimic_1&&+shiny_sword&You kick the mimic, and it dies.\n&t1&"
                           "&ishiny_sword.ascii&The chest opens to reveal a shining sword.\n&t1&&spickup.wav&"
                           "You take it.>&=mimic_2&<&-mimic_2&&+mimic_1&>&=mimic_3&<&-mimic_3&&+mimic_2&>"
                           "&=mimic_4&<&-mimic_4&&+mimic_3&>&!shiny_sword&<"
                           "&=mimic_kick&<&+death&You kick it again, but it knows your tricks.\n&t1&"
                           "It bites your leg and it starts bleeding.\n&t2&Badly.\n&t2&&ideath.ascii&You die.>"
                           "&!mimic_kick&<&-mimic_punch&&+mimic_kick&You kick the mimic, but it fights back.\n&t1&"
                           "&r&&=random&<&r&&=random&<You barely survive.>"
                           f"&!random&<{player_lose_health}You lose 1 HP.>&+random&>"
                           f"&!random&<{player_lose_health}You lose 1 HP.>>>", "image": "mimic.ascii",
                   "sound": "chest_kick.wav",
                   "options": [("The end", "", "ending", "=death"),
                               ("Punch the mimic", "punch", "punch_mimic", "!death", "!shiny_sword"),
                               ("Kick the mimic", "kick", "kick_mimic", "!death", "!shiny_sword"),
                               ("Go through the tunnel", ("tunnel", ""), "tunnel", "=shiny_sword")],
                   "hiddenoptions": hidden},
    "tunnel": {"text": "You go into the tunnel.\n&t1&After walking for a small time, you see something.\n&t1&"
                       "&isword.ascii&In the middle of the tunnel, there is a sword.", "image": "tunnel.ascii",
               "options": [("Take it", ("take", "take it"), "tunnel_take"),
                           ("Ignore it", "ignore", "tunnel_ignore", "!shiny_sword"),
                           ("Ignore it - I already have a sword much better!", "ignore", "tunnel_ignore",
                            "=shiny_sword")], "hiddenoptions": hidden},
    "tunnel_take": {"text": "&+sword&&spickup.wav&You take the sword.", "image": "sword.ascii",
                    "options": [("Continue", ("continue", ""), "tunnel_end")], "hiddenoptions": hidden},
    "tunnel_ignore": {"text": "You ignore the sword.", "image": "sword.ascii",
                      "options": [("Continue", ("continue", ""), "tunnel_end")], "hiddenoptions": hidden},
    "tunnel_end": {"text": "&+boss&&+boss_10&You walk through the tunnel for some time.\n&t2&"
                           "You finally see it's end.\n&t2&&iboss_entrance.ascii&"
                           "You see a giant room, with an... egg? sitting on a throne, "
                           "surrounded by two guards with spears.\n&t1&The guards say: Kevin, someone's here!",
                   "image": "tunnel.ascii",
                   "options": [("Try to run", "run", "run_boss"),
                               ("Pull out the sword", "sword", "boss_sword", "=sword"),
                               ("Pull out the shiny sword", ("shiny", "shiny sword"), "boss_shiny_sword",
                                "=shiny_sword"), ("Punch the egg", "punch", "boss_punch"),
                               ("Try to negotiate", "negotiate", "boss_negotiate")],
                   "hiddenoptions": hidden},
    "run_boss": {"text": "You try to run back&=try_run&< again>.\n&t2&&iboss_runs.ascii&"
                         f"But the giant egg runs towards you.\n&w&&!try_run&<{player_lose_health * 2}You lose 2 HP.>"
                         "&=try_run&<&+death&No luck this time, though.>&=death&<\nYou die.>&+try_run&",
                 "image": "run_from_boss.ascii",
                 "options": [("Pull out the sword", "sword", "boss_sword", "=sword", "!sword_out", "!death"),
                             ("Use the sword", "sword", "boss_sword", "=sword", "=sword_out", "!death"),
                             ("Pull out the shiny sword", ("shiny", "shiny sword"), "boss_shiny_sword",
                              "=shiny_sword", "!shiny_sword_out", "!death"),
                             ("Use the shiny sword", ("shiny", "shiny sword"), "boss_shiny_sword", "=shiny_sword",
                              "=shiny_sword_out", "!death"), ("Punch the egg", "punch", "boss_punch", "!death"),
                             ("Try to negotiate", "negotiate", "boss_negotiate", "!death"),
                             ("The end", "", "ending", "=death")], "hiddenoptions": hidden},
    "boss_sword": {"text": "&-guards_off_guard&&!sword_out&<&ssword_out.wav&You pull out your sword.\n&t1&"
                           "The guards start laughing&!orb_curse&<.>&=orb_curse&<: So this is what we prepared for?>"
                           f"&+guards_off_guard&>&=sword_out&<&sslash.wav&&r&&=random&<{boss_lose_health}"
                           "You slash with your sword.\n&t1&The egg loses 1 HP.>&!random&<"
                           "You slash with the sword, but you deal no damage.>\n&t1&&r&&=random&<"
                           f"{player_lose_health}You lose 1 HP.>&!random&<&r&&=random&<"
                           f"{player_lose_health}You lose 1 HP.>&!random&<{player_lose_health * 2}You lose 2 HP.>>>"
                           "&=boss_0&<\n&t1&The egg dies.\n&t1&The guards, scared, run away.\n&t1&"
                           "&=death&<&+heroic&But you die in the process.>&!death&<You win!>>&!boss_0&<&=death&<"
                           "\n&t1&&ideath.ascii&You die.>>"
                           "&+sword_out&", "image": "boss_room.ascii",
                   "options": [("Use the guards laughing and catch them off guard", ("guards", "catch", "off guard"),
                                "boss_guards_off_guard", "=guards_off_guard", "!boss_0", "!death"),
                               ("Try to run", "run", "run_boss", "!boss_0", "!death"),
                               ("Use the sword again", "sword", "boss_sword", "=sword", "!guards_off_guard",
                                "!boss_0", "!death"), ("Pull out the shiny sword", ("shiny", "shiny sword"),
                                                       "boss_shiny_sword", "=shiny_sword", "!shiny_sword_out",
                                                       "!boss_0", "!death"),
                               ("Use the shiny sword", ("shiny", "shiny sword"), "boss_shiny_sword", "=shiny_sword",
                                "=shiny_sword_out", "!boss_0", "!death"), ("Punch the egg", "punch", "boss_punch",
                                                                           "!boss_0", "!death"),
                               ("Try to negotiate", "negotiate", "boss_negotiate", "!boss_0", "!death"),
                               ("The end.", "", "ending", "=boss_0", "!death"), ("The end.", "", "ending", "=death")],
                   "hiddenoptions": hidden},
    "boss_guards_off_guard": {"text": f"{boss_lose_health * 2}You use the opportunity and rush the egg.\n&t1&"
                                      "&sslash.wav&It loses 2 HP.&=boss_0&<\n&t1&The egg dies.\n&t1&"
                                      "The guards, scared, run away.\n&t1&You win!>", "image": "boss_room.ascii",
                              "options": [("Use the sword again", "sword", "boss_sword", "=sword", "!boss_0"),
                                          ("Pull out the shiny sword", ("shiny", "shiny sword"), "boss_shiny_sword",
                                           "=shiny_sword", "!shiny_sword_out", "!boss_0"),
                                          ("Use the shiny sword", ("shiny", "shiny sword"), "boss_shiny_sword",
                                           "=shiny_sword", "=shiny_sword_out", "!boss_0"),
                                          ("Punch the egg", "punch", "boss_punch", "!boss_0"),
                                          ("The end.", "", "ending", "=boss_0")], "hiddenoptions": hidden},
    "boss_shiny_sword": {"text": f"&-guards_off_guard&&!shiny_sword_out&<&ssword_out.wav&{boss_lose_health * 3}"
                                 "You pull out your shiny sword.\n&t1&The guards are mesmorized.\n&t1&"
                                 "&sslash.wav&You slash with the sword and the egg loses 3 HP.&+guards_off_guard&>"
                                 f"&=shiny_sword_out&<&sslash.wav&You slash with your sword.\n&t1&&r&&=random&<"
                                 f"{boss_lose_health * 2}The egg loses 2 HP.>&!random&<{boss_lose_health}"
                                 f"The egg loses 1 HP.>\n&t1&&r&&=random&<{player_lose_health}You lose 1 HP.>"
                                 f"&!random&<{player_lose_health * 2}You lose 2 HP.>>&=boss_0&<\n&t1&The egg dies."
                                 "\n&t1&The guards, scared, run away.\n&t1&&=death&<&+heroic&"
                                 "But you die in the process.>&!death&<You win!>>&=death&<\n&t1&&ideath.ascii&You die.>"
                                 "&+shiny_sword_out&", "image": "boss_room.ascii",
                         "options": [
                             ("Pull out the sword", "sword", "boss_sword", "=sword", "!sword_out", "!boss_0", "!death"),
                             ("Use the sword", "sword", "boss_sword", "=sword", "=sword_out", "!boss_0", "!death"),
                             ("Use the shiny sword again", ("shiny", "shiny sword"), "boss_shiny_sword", "=shiny_sword",
                              "=shiny_sword_out", "!boss_0", "!death"), ("Punch the egg", "punch", "boss_punch",
                                                                         "!boss_0", "!death"),
                             ("The end.", "", "ending", "=boss_0", "!death"), ("The end", "", "ending", "=death")],
                         "hiddenoptions": hidden},
    "boss_punch": {"text": "You try to punch the egg, but the guards stop you.\n&t1&They run after you.\n&t1&&+death&"
                           "&ideath.ascii&You die.", "image": "boss_room.ascii",
                   "options": [("The end.", "", "ending")], "hiddenoptions": hidden},
    "boss_negotiate": {"text": "You try to negotiate.\n&t2&But the giant egg doesn't listen.\n&t2&"
                               "The guards run after you.\n&t1&&+death&&ideath.ascii&You die.",
                       "image": "boss_room.ascii", "options": [("The end.", "", "ending")], "hiddenoptions": hidden},
    "ending": {"text": "&=death&<&ideath.ascii&You died to &!boss&<the mimic>&=boss&<the egg&=heroic&< heroically>>.>"
                       "&!death&<&iwin.ascii&You won!\n&t1&Your achievements:"
                       "&=letter&<\nI knew about everything beforehand...>&=fair_door&<\nI'm kicking no doors!>"
                       "&!fair_door&<\nDoor kicker!>&=orb_curse&<\nCurious>&=shiny_sword&<\nFighter"
                       "&=sword&<\nDouble swords!>>&=sword_out&<&=shiny_sword_out&<\nDouble wield!>>"
                       "&=try_run&<\nRunner>&w&&isilaeder.ascii&&w&&isilaeder.ascii&&w&&isilaeder.ascii&"
                       "&w&&isilaeder.ascii&&w&&isilaeder.ascii&&w&>",
               "options": [("End", "", "end")], "hiddenoptions": hidden}
}
