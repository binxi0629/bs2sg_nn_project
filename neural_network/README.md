# Note

### Setup

inside `root/`, create folders `data/` for storing all data

inside `data/`, create folders `actual/` for storing target data

inside `data/`, create folders `guess/` for storing generated data

---

to create target data inside `actual/` for training

edit `main.py` and run the following lines **once**

    data_processing.create_valid_list_files(30, "data/new_input_data_2/", "data/actual/valid_list.txt")
    data_processing.create_actual_crystal_list_files("data/actual/valid_list.txt", "data/actual/")
    data_processing.create_actual_spacegroup_list_files("data/actual/valid_list.txt", "data/actual/")

---

input data can be downloaded [here](https://drive.google.com/drive/folders/125nuunU1Y2Tokx86SW87v91MKNJplH07)

put the folder containing json files into `data/`

---

here is the final folder structure after training

    root/
    ├── data/
    |   ├── actual/
    |   |   ├── crystal_list_*.txt
    |   |   ├── spacegroup_list*.txt
    |   |   └── valid_list.txt
    |   ├── guess/
    |   |   ├── crystal_list_*.txt
    |   |   └── spacegroup_list*.txt
    |   └── input_data/
    |       └── *.json
    ├── analysis.py
    ├── base_model.py
    ├── crystal.py
    ├── data_loader.py
    ├── data_processing.py
    ├── main.py
    ├── network.py
    └── README.md
    
---

*\* some of the files are ignored and haven't been uploaded onto github.
This causes error when python tries to create files inside ignored folders.*