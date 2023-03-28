jitcount = 0

with open('jitpass.log', 'r',encoding = "ISO-8859-1") as f:

    for line in f:
        if 'completed compiling' in line:
            jitcount += 1

print(f'The phrase "completed compiling" appears {jitcount} times in the text file.')
