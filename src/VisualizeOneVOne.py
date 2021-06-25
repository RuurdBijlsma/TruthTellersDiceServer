import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb

with open("OneVOne.txt", "r") as thisfile:
    lines = thisfile.readlines()
    # If player 1 challenges
    challengemat1 = np.zeros([3,3])
    # If player 2 challenges
    challengemat2 = np.zeros([3,3])
    successmat1 = np.zeros([3,3])
    successmat2 = np.zeros([3,3])
    successratemat1 = np.zeros([3,3])
    successratemat2 = np.zeros([3,3])
    for line in lines:
        line = line.strip("]\n").strip("]").strip("[")
        splitline = line.split(",")
        t1 = str(splitline[0]).strip().strip("\'").strip()
        t2 = str(splitline[1]).strip().strip("\'").strip()
        cht1 = int(splitline[2])
        cht2 = int(splitline[3])
        st1 = int(splitline[4])
        st2 = int(splitline[5])
        rownames = ["Highest", "Random", "Lowest"]
        colnames = ["Highest", "Random", "Lowest"]

        for i, rowname in enumerate(rownames):
            for j, colname in enumerate(colnames):
                if t1 == rowname and t2 == colname:
                    challengemat1[i,j] += cht1
                    challengemat2[i,j] += cht2
                    successmat1[i,j] += st1
                    successmat2[i,j] += st2
    successratemat1 = np.divide(successmat1,challengemat1)
    successratemat2 = np.divide(successmat2,challengemat2)

    plt.figure(1)
    plt.title("Successrate of player 1 challenging player 2")
    sb.heatmap(successratemat1, yticklabels=rownames, xticklabels=colnames)
    plt.ylabel("Tactic player 1")
    plt.xlabel("Tactic player 2")
    plt.figure(2)
    plt.title("Successrate of player 2 challenging player 1")
    sb.heatmap(successratemat2, yticklabels=rownames, xticklabels=colnames)
    plt.ylabel("Tactic player 1")
    plt.xlabel("Tactic player 2")
    plt.show()









