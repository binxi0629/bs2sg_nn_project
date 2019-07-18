import json, os, shutil
from pathlib import Path

from diagnosis import diagnosis


def filter_from_weight(data_dir, database_dir, weight_limit=100):
    count = 1
    low_weights_list = {}

    # stat sg_weights before adding in data
    sg_weights = diagnosis.count_spacegroup_weights(data_dir='../data/', plt=True)

    for num in range(len(sg_weights)):
        if sg_weights[num][1] < weight_limit:
            low_weights_list[sg_weights[num][0]] = sg_weights[num][1]

    for subdir, dirs, files in os.walk(database_dir):
        num_files = len(files)
        for i in range(num_files):
            with open(database_dir+files[i], 'r') as f:
                data = json.load(f)
                sg_number = data['number']

            if sg_number in low_weights_list.keys():
                file = Path(data_dir+files[i])
                if file.exists():
                    pass
                else:
                    shutil.copy2(database_dir+files[i], data_dir)
                    count += 1
                    print('\rCopied {file_name}, {count}'.format(file_name=files[i], count=count), end='')

    sg_weights = diagnosis.count_spacegroup_weights(data_dir='../data/', plt=True)


if __name__ == '__main__':
    filter_from_weight(data_dir='../data/', database_dir='../current_data/', weight_limit=100)