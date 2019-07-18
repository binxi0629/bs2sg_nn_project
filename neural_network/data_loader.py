import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
import json
import numpy

import crystal


class SetBs2Sg(Dataset):
    def __init__(self, list_paths, valid_size):
        data_input_valid = []
        data_label_valid = []
        data_input_train = []
        data_label_train = []
        import os
        for j, list_path in enumerate(list_paths):
            if os.stat(list_path).st_size == 0:
                continue
            file_name_arr = numpy.loadtxt(list_path, "U60", ndmin=1)
            cur_len = file_name_arr.size
            numpy.random.shuffle(file_name_arr)
            split = int(numpy.floor(valid_size * cur_len))
            for i in range(cur_len):
                file_name = file_name_arr[i]
                with open(file_name, "r") as file:
                    data_json = json.load(file)
                    data_input_np = numpy.array(data_json["bands"])
                    data_input_np = data_input_np.flatten().T
                    sgnum = data_json["number"]

                    data_label = sgnum - 1

                    data_label_np = numpy.array([data_label])
                if i < split:
                    data_input_valid.append(torch.from_numpy(data_input_np).float())
                    data_label_valid.append(torch.from_numpy(data_label_np).long())
                else:
                    data_input_train.append(torch.from_numpy(data_input_np).float())
                    data_label_train.append(torch.from_numpy(data_label_np).long())
            print("\r\tload: {}/{}".format(j, len(list_paths)), end="")
        print("\rload: {}".format(len(list_paths)))
        self.data_inputs = data_input_valid + data_input_train
        self.data_labels = data_label_valid + data_label_train
        self.len = len(self.data_inputs)
        self.valid_size = valid_size

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        return self.data_inputs[index], self.data_labels[index]


class SetBs2Cs(Dataset):
    def __init__(self, list_paths, valid_size):
        data_input_valid = []
        data_label_valid = []
        data_input_train = []
        data_label_train = []
        import os
        for j, list_path in enumerate(list_paths):
            if os.stat(list_path).st_size == 0:
                continue
            file_name_arr = numpy.loadtxt(list_path, "U60", ndmin=1)
            cur_len = file_name_arr.size
            numpy.random.shuffle(file_name_arr)
            split = int(numpy.floor(valid_size * cur_len))
            for i in range(cur_len):
                file_name = file_name_arr[i]
                with open(file_name, "r") as file:
                    data_json = json.load(file)
                    data_input_np = numpy.array(data_json["bands"])
                    data_input_np = data_input_np.flatten().T
                    sgnum = data_json["number"]

                    data_label = crystal.crystal_number(sgnum) - 1

                    data_label_np = numpy.array([data_label])
                if i < split:
                    data_input_valid.append(torch.from_numpy(data_input_np).float())
                    data_label_valid.append(torch.from_numpy(data_label_np).long())
                else:
                    data_input_train.append(torch.from_numpy(data_input_np).float())
                    data_label_train.append(torch.from_numpy(data_label_np).long())
            print("\r\tload: {}/{}".format(j, len(list_paths)), end="")
        print("\rload: {}".format(len(list_paths)))
        self.data_inputs = data_input_valid + data_input_train
        self.data_labels = data_label_valid + data_label_train
        self.len = len(self.data_inputs)
        self.valid_size = valid_size

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        return self.data_inputs[index], self.data_labels[index]


class SetCs2Sg(Dataset):
    def __init__(self, list_paths, csnum, valid_size):
        data_input_valid = []
        data_label_valid = []
        data_input_train = []
        data_label_train = []
        import os
        for j, list_path in enumerate(list_paths):
            if os.stat(list_path).st_size == 0:
                continue
            file_name_arr = numpy.loadtxt(list_path, "U60", ndmin=1)
            cur_len = file_name_arr.size
            numpy.random.shuffle(file_name_arr)
            split = int(numpy.floor(valid_size * cur_len))
            for i in range(cur_len):
                file_name = file_name_arr[i]
                with open(file_name, "r") as file:
                    data_json = json.load(file)
                    data_input_np = numpy.array(data_json["bands"])
                    data_input_np = data_input_np.flatten().T
                    sgnum = data_json["number"]

                    crystal_lower = crystal.spacegroup_index_lower(csnum)
                    crystal_upper = crystal.spacegroup_index_upper(csnum)
                    crystal_size = crystal_upper - crystal_lower
                    if sgnum not in range(crystal_lower + 1, crystal_upper + 1):
                        data_label = crystal_size  # unclassified / rejected
                    else:
                        data_label = sgnum - crystal_lower - 1

                    data_label_np = numpy.array([data_label])
                if i < split:
                    data_input_valid.append(torch.from_numpy(data_input_np).float())
                    data_label_valid.append(torch.from_numpy(data_label_np).long())
                else:
                    data_input_train.append(torch.from_numpy(data_input_np).float())
                    data_label_train.append(torch.from_numpy(data_label_np).long())
            print("\r\tload: {}/{}".format(j, len(list_paths)), end="")
        print("\rload: {}".format(len(list_paths)))
        self.data_inputs = data_input_valid + data_input_train
        self.data_labels = data_label_valid + data_label_train
        self.len = len(self.data_inputs)
        self.valid_size = valid_size

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        return self.data_inputs[index], self.data_labels[index]


def get_valid_train_loader(dataset,
                           batch_size):
    num_train = len(dataset)
    indices = list(range(num_train))
    split = int(numpy.floor(dataset.valid_size * num_train))

    valid_idx, train_idx = indices[:split], indices[split:]

    valid_sampler = SubsetRandomSampler(valid_idx)
    train_sampler = SubsetRandomSampler(train_idx)

    valid_loader = DataLoader(
        dataset, batch_size=batch_size, sampler=valid_sampler,
    )
    train_loader = DataLoader(
        dataset, batch_size=batch_size, sampler=train_sampler,
    )

    return valid_loader, train_loader


if __name__ == '__main__':
    # bs2sg = SetBs2Sg(["data/actual/spacegroup_list_{}.txt".format(i) for i in range(1, 231)], 0.1)
    # bs2cs = SetBs2Cs(["data/actual/crystal_list_{}.txt".format(i) for i in range(1, 8)], 0.1)
    # for c in range(1, 8):
    #     cs2sg = SetCs2Sg(["data/actual/spacegroup_list_{}.txt".format(i) for i in
    #                           crystal_functions.spacegroup_number_range(c)], c, 0.1)
    pass