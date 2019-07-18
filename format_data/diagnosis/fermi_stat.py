import json
import os
import numpy as np


def fermi_level_stat():
    data_dir = "../../data/"
    fermi_stat_res = []
    for subdir, dirs, files in os.walk(data_dir):
        num_files = len(files)
        for i in range(num_files):
            with open(data_dir+files[i]) as f:
                data_json = json.load(f)

            bands = data_json["band"]["bands"]
            bands = np.array(bands)
            # count the total bands number - 1
            bands_num = np.shape(bands)[0]

            # locate the position of fermi level
            fermi_index = 0
            for j in range(bands_num):
                if (bands[j][0])*(bands[j+1][0]) <= 0:
                    fermi_index = j
                    break
                else:
                    pass
            fermi_stat_res.append([i+1, bands_num+1, fermi_index+1])
            print("Finished ... {i}/{len}".format(i=i+1, len=num_files))

    fermi_stat_res = np.int_(fermi_stat_res)
    print(np.shape(fermi_stat_res[0]))

    with open("fermi_stat_res.json", 'w') as outfile:
        json.dump(fermi_stat_res, outfile, cls=NumpyEncoder, indent=2)


def fermi_stat_less_than_15():
    with open('fermi_stat_res.json', 'r') as f:
        data = json.load(f)

    data = np.array(data)
    new_data = []
    num = np.shape(data)[0]
    for i in range(num):
        if data[i, 2] <= 15:
            new_data.append(data[i, :])
            print("Finished {}".format(i))

    with open('fermi_stat_less_than_15.json', 'w') as outfile:
        json.dump(new_data, outfile, cls=NumpyEncoder, indent=2)


class NumpyEncoder(json.JSONEncoder):
    """
        to solve Error: NumPy array is not JSON serializable
        see: https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    # fermi_level_stat()
    fermi_stat_less_than_15()