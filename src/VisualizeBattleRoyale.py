import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb

with open("Battleroyale.txt", "r") as thisfile:
    lines = thisfile.readlines()
    tactics = ["Random", "Highest", "Lowest"]
    challenges = np.zeros(len(tactics))
    successes = np.zeros(len(tactics))
    challengeposition = np.zeros(4)
    successperposition = np.zeros(4)

    for line in lines:
        line = line.strip("]\n").strip("]").strip("[")
        splitline = line.split(",")
        t1 = str(splitline[0]).strip().strip("\'").strip()
        t2 = str(splitline[1]).strip().strip("\'").strip()
        t3 = str(splitline[2]).strip().strip("\'").strip()
        t4 = str(splitline[3]).strip().strip("\'").strip()
        cht1 = int(splitline[4])
        cht2 = int(splitline[5])
        cht3 = int(splitline[6])
        cht4 = int(splitline[7])
        st1 = int(splitline[8])
        st2 = int(splitline[9])
        st3 = int(splitline[10])
        st4 = int(splitline[11])

        tacticlist = [t1, t2, t3, t4]
        challengelist = [cht1, cht2, cht3, cht4]
        successlist = [st1, st2, st3, st4]

        challengeposition = challengeposition + np.array(challengelist)
        successperposition = successperposition + np.array(successlist)

    print("Challenges per position")
    print(challengeposition)
    print("Successes per position")
    print(successperposition)
    print("Successful challenge ratio per position")
    print(np.divide(successperposition,challengeposition))


challengemat = np.zeros([3,3])
with open("broyal.txt", "r") as broy:
    lines = broy.readlines()
    for i in range(6,9):
        c1 = lines[i].strip().strip("[").strip("]").split(" ")
        somestuff = []
        for thing in c1:
            if thing:
                somestuff.append(float(thing))
        challengemat[i-6,:] = np.array(somestuff)


rownames = ["Highest", "Random", "Lowest"]
plt.figure(1)
plt.title("Ratio of successful challenges")
sb.heatmap(challengemat, yticklabels=rownames, xticklabels=rownames)
plt.ylabel("Tactic challenging player")
plt.xlabel("Tactic defending player")
plt.show()








