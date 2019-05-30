import pypokedex
with open("pkmnBasicInfo.txt", "a") as f:
    for num in range(1, 152):
        basicInfo = pypokedex.get(dex=num)
        f.write(basicInfo.name.capitalize() + " ")
        for stat in basicInfo.base_stats:
            f.write(str(stat) + " ")
        for move in basicInfo.moves["firered-leafgreen"]:
            f.write(move.name + " " + str(move.level) + " ")
        f.write("\n")