import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

tips = sns.load_dataset("tips")

# Average tip per day
avg_tip = tips.groupby("day")["tip"].mean()

# Line graph
avg_tip.plot(kind="line", marker="o")
plt.xlabel("Day")
plt.ylabel("Average Tip")
plt.title("Average Tip Amount for Each Day")
plt.show()

# Highest average tip day
highest_day = avg_tip.idxmax()
print("Day with highest average tip:", highest_day)