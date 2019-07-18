import json
import os
import numpy as np
from utils import plot_tool


def count_spacegroup_weights(data_dir='../../input_data_test02/', plt=False):

    # initialize sg_weight
    sg_weights = np.zeros([230, 2])
    for i in range(230):
        sg_weights[i][0] = i+1

    for subdir, dirs, files in os.walk(data_dir):
        num_files = len(files)
        for i in range(num_files):
            with open(data_dir+files[i]) as f:
                data_json = json.load(f)
                sg_number = np.array(data_json["number"])
                sg_weights[sg_number-1][1] += 1
    sg_weights = np.int_(sg_weights)

    # print(sg_weights)

    if plt:
        plot_tool.plot(x_data=sg_weights[:, 0],
                       y_data=sg_weights[:, 1],
                       x_label="spacegroup number",
                       y_label="occurrence",
                       y_limit=500,
                       title="Occurrence for spacegroup number",
                       bar=True)

    # sg_number-1, count
    return sg_weights


def check_specific_spacegroup_num(data_dir, occurrence_limit=50, greater=False, save=False, plt=False):
    # initialize sg_weight
    sg_weights = count_spacegroup_weights(data_dir, plt=plt)
    count = 0
    res = []
    for i in range(230):
        if greater:
            if sg_weights[i, 1] >= occurrence_limit:
                count += 1
                res.append(sg_weights[i, 0])
        else:
            if sg_weights[i, 1] < occurrence_limit:
                count += 1
                res.append(sg_weights[i, 0])
    if save:
        with open('sg_working_list.json', 'w') as f:
            json.dump(res, f, cls=NumpyEncoder, indent=2)

    return res, count


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
    """count_result, count = check_specific_spacegroup_num(data_dir='../../new_input_data_5/',
                                                        occurrence_limit=100,
                                                        greater=True,
                                                        save=False, plt=True)
    """
    sg_weight = count_spacegroup_weights(plt=True)
    data = {}

    data["sg_weights"] = sg_weight
    with open("sg_weights.json", 'w') as f:
        json.dump(data, f, cls=NumpyEncoder, indent=2)
