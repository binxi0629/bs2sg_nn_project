import format_data
import os
import json
import numpy as np
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt


def statistic():
    data_dir = '../data/'
    stat_res = {}

    for subdir, dirs, files in os.walk(data_dir):
        num_files = len(files)
        for i in range(num_files):
            with open(data_dir+files[i]) as f:
                data_json = json.load(f)

                this_id = "mp_{}".format(data_json["id"])
                stat_res[this_id] = {}

                stat_res[this_id][this_id] = data_json["formula"]
                stat_res[this_id]['num_sites'] = data_json["num_sites"]

                stat_res[this_id]['bands'] = {}
                total_bands = np.shape(np.array(data_json["band"]["bands"]))

                stat_res[this_id]['bands']['total_bands'] = total_bands[0]

                stat_res[this_id]['bands']['branches'] = {}
                stat_res[this_id]['bands']['branches'] = data_json["band"]["branches"]
                print("finished:{this_num}/{total_num}".format(this_num=i+1, total_num=num_files))

    with open('stat_res.json', 'w') as f:
        json.dump(stat_res, f, cls=format_data.NumpyEncoder, indent=4)


def stat_bands():
    with open("stat_res.json", 'r') as f:
        data = json.load(f)

    save_plot_data = {}
    save_plot_data["bands"] = []

    for i in data:
        save_plot_data["bands"].append(data[i]["bands"]["total_bands"])

    with open('plot_data.json', 'w') as f:
        json.dump(save_plot_data, f, cls=format_data.NumpyEncoder, indent=2)


def plot_bands():
    with open("plot_data.json", 'r') as f:
        bands_info = json.load(f)

    tmp = bands_info["bands"]

    res = Counter(tmp)
    new_plot = {}
    new_plot["bands_info"] =[]
    for x in res:
        new_plot["bands_info"].append({"bands": x, "weights": res[x]})

    df = pd.DataFrame(new_plot["bands_info"])
    print(df)
    # df.plot()
    plot = df.plot.bar(x='weights', y='bands')
    # fig = plot.get_figure()
    # fig.savefig('bands_info.png')
    # plt.show()
    # with open('bands_res.json', 'w') as f:
    #    json.dump(res, f, cls=format_data.NumpyEncoder, indent=2)


class NumpyEncoder(json.JSONEncoder):
    """
        to solve Error: NumPy array is not JSON serializable
        see: https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


if __name__ == '__main__':
    statistic()
    # plt.close("all")
    # plot_bands()

