import os
import json
import pandas as pd
import matplotlib.pyplot as plt

script_directory = os.path.abspath(os.path.dirname(__file__))

counts = {}

def load_stats():
    global counts
    try:
        with open('imagestats.json', 'r') as json_file:
            counts = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        counts = {}

def save_stats(stats):
    with open('forPandas.json', 'w') as json_file:
        json.dump(stats, json_file)

def removeDir():
    newCounts = {}
    for k,v in counts.items():
        newKey = k[43:]
        newCounts.update({newKey[:-4]: int(v)})
    return newCounts
    
def jsonToDataFrame():
    series = pd.read_json('forPandas.json', typ='series', orient='index')
    frame = series.to_frame(name="# Rolls")
    return frame

def sortVals(df):
    df

if __name__ == "__main__":
    load_stats()
    save_stats(removeDir())
    characterStats = jsonToDataFrame()
    print(characterStats[characterStats["# Rolls"] < 1])
    characterStats.sort_values(by="# Rolls", ascending=False).head(40).plot.bar()
    plt.show()
