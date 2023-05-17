turntables = [":black_large_square:"] * 3
turntable_list = [
    ":cherries:",
    ":apple:",
    ":star:",
    ":gem:",
    ":coin:",
    ":moneybag: ",
]
graphic_dict = {
    "Green": ":green_square:",
    "Blue": ":blue_square:",
    "Left_arrow": ":arrow_left:",
    "Right_arrow": ":arrow_right:",
    "turntables": "".join(turntables),
}
content = "{Blue}{Green}{Green}{Green}{Blue}\n{Right_arrow}{turntables}{Left_arrow}\n{Blue}{Green}{Green}{Green}{Blue}".format(
    **graphic_dict
)
print(content)
