# Open the file
with open("players.txt", "r") as file:
    lines = file.readlines()

# Modify the positions (L -> LW, R -> RW)
modified_lines = []
for line in lines:
    line = line.replace(" L ", " LW ")  # Change 'L' to 'LW'
    line = line.replace(" R ", " RW ")  # Change 'R' to 'RW'
    modified_lines.append(line)

# Sort the lines by team abbreviation and then by last name
modified_lines.sort(key=lambda x: (x.split(" | ")[0]))

with open("players_modified.txt", "w") as file:
    file.writelines(modified_lines)