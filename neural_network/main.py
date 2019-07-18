import numpy

import torch
import torch.nn
import torch.nn.functional

import data_processing
import base_model
import data_loader
import network
import crystal
import analysis


# bandstructure to spacegroup
def main_bs2sg(num_epoch: int = 1):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = base_model.get_bs2sg()
    model = model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.75)
    criterion = torch.nn.CrossEntropyLoss()

    dataset = data_loader.SetBs2Sg(["data/actual/spacegroup_list_{}.txt".format(i) for i in range(1, 231)], 0.1)
    train_loader, valid_loader = data_loader.get_valid_train_loader(dataset, 32)

    network.validate_train_loop(
        device, model, optimizer, scheduler, criterion, valid_loader, train_loader, num_epoch
    )

    data_processing.create_empty_list_files(230, "data/guess/", "spacegroup_list_{}.txt")
    data_processing.create_guess_list_files(
        device, model, 230, "data/actual/valid_list.txt", "data/guess/", "spacegroup_list_{}.txt"
    )


# bandstructure to crystal system
def main_bs2cs(num_epoch: int = 1):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = base_model.get_bs2cs()
    model = model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.75)
    criterion = torch.nn.CrossEntropyLoss()

    dataset = data_loader.SetBs2Cs(["data/actual/crystal_list_{}.txt".format(i) for i in range(1, 8)], 0.1)
    train_loader, valid_loader = data_loader.get_valid_train_loader(dataset, 32)

    network.validate_train_loop(
        device, model, optimizer, scheduler, criterion, valid_loader, train_loader, num_epoch
    )

    data_processing.create_guess_list_files(
        device, model, 7, "data/actual/valid_list.txt", "data/guess/", "crystal_list_{}.txt"
    )


# 1 crystal system to spacegroup in that crystal system
def main_cs2sg_one(csnum: int, model_struct: tuple, num_epoch: int = 1):
    print("crystal system: {}".format(csnum))
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = base_model.get_cs2sg(
        *model_struct
    )
    model = model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.75)
    criterion = torch.nn.CrossEntropyLoss()

    dataset = data_loader.SetCs2Sg(["data/actual/spacegroup_list_{}.txt".format(i) for i in
                                    crystal.spacegroup_number_range(csnum)], csnum, 0.1)

    train_loader, valid_loader = data_loader.get_valid_train_loader(dataset, 32)

    network.validate_train_loop(
        device, model, optimizer, scheduler, criterion, valid_loader, train_loader, num_epoch
    )

    data_processing.append_guess_spacegroup_in_crystal_list_files(
        device, model, csnum, "data/guess/crystal_list_{}.txt".format(csnum), "data/guess/"
    )


# crystal system to spacegroup
def main_cs2sg_all(num_epoch: int = 1):
    data_processing.create_empty_list_files(230, "data/guess/", "spacegroup_list_{}.txt")

    input_sizes = [800, 2800, 2100, 1000, 1300, 600, 1100]*7
    cs_sizes = crystal.crystal_system_sizes()
    output_sizes = [cs_sizes[i - 1] - cs_sizes[i - 2] + 1 if i > 1 else 3 for i in range(1, 8)]

    for i in range(1, 8):
        main_cs2sg_one(i, (input_sizes[i], 128, 128, output_sizes[i]), num_epoch)


if __name__ == "__main__":
    # my_seed = 1155110044
    # numpy.random.seed(my_seed)
    # torch.manual_seed(my_seed)

    # prepare input data #
    # data_processing.create_valid_list_files(100, "data/input_data_test01/", "data/actual/valid_list.txt")
    # TODO: try the following line, use it after (bs2cs + formated data) or (bs2cs)
    # data_processing.create_7_valid_list_files(100, "data/cs_data/cs_{}_input_data/",
    #                                           "data/guess/", "cs_{}_valid_list.txt")

    # prepare actual data # (Do this everytime dataset is changed)
    # data_processing.create_actual_crystal_list_files("data/actual/valid_list.txt", "data/actual/")
    # data_processing.create_actual_spacegroup_list_files("data/actual/valid_list.txt", "data/actual/")

    # generate guess data #
    # main_bs2sg(num_epoch=10)
    # main_bs2cs(num_epoch=20)
    # TODO: try the following line, same as before but make sure to hard code in the input_sizes array in main_cs2sg_all
    main_cs2sg_all(num_epoch=20)

    # analyse result #
    # analysis.print_result(range(1, 8), "data/guess/", "data/actual/", "crystal_list_{}.txt")  # into cs
    # analysis.print_result(range(1, 231), "data/guess/", "data/actual/", "spacegroup_list_{}.txt")  # into sg
    # for c in range(1, 8):  # into cs and sg
    #     print("crystal system {}".format(c))
    #     print("\nbandstructure to crystal system result")
    #     analysis.print_result(
    #         [c], "data/guess/", "data/actual/", "crystal_list_{}.txt"
    #     )
    #     print("\ncrystal to spacegroup system result")
    #     analysis.print_result(
    #         crystal.spacegroup_number_range(c), "data/guess/", "data/actual/", "spacegroup_list_{}.txt"
    #     )
    #     print("\n")

    torch.cuda.empty_cache()
    import winsound
    duration = 500  # milliseconds
    freq = 200  # Hz
    winsound.Beep(freq, duration)