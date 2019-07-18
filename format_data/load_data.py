from pymatgen.ext.matproj import MPRester
from diagnosis import diagnosis
import format_data
import json, os, re
import numpy as np


m = MPRester("z9urSTLgyAmN85OW")


def get_space_group_from_file(mp_id):  # load file in input_data
    try:
        with open('../input_data/input_data_{}.json'.format(mp_id), 'r') as f:
            doc = json.load(f)
        return doc["spacegroup"], doc["number"]
    except FileNotFoundError:
        return


def create_new_data(data_dir='../data/',
                    crystal_system='0',
                    degeneracy=False,
                    en_tolerance=0.01,
                    around_fermi=False,
                    b2t=False,
                    padding_b2t=False,
                    padding_around_fermi=False,
                    # padding_num=9999,
                    num_of_bands=30,
                    bands_below_fermi_limit=15,
                    save_dir="../input_data_3/"):
    """
        data_dir: raw data directory
        degeneracy: if doing degeneracy translation, default: False
        en_tolerance: degenerate if energy difference between two bands smaller than en_tolerance, default: 0.01
        around_fermi: if the bands are around fermi, default: False
        num_of_bands: number of bands, default: 30
        bands_below_fermi_limit, related to (half of) num_of_bands
        save_dir: saving the new formatted input data to which directory

        *Note:
            required directory: raw data directory
                         input_data directory
    """

    data = {}
    data["number"] = 0
    data["spacegroup"] = None
    count = 1
    error_files = {}
    error_files["mp_id"] = []
    low_fermi = []

    print("Loading... Please wait")

    for subdir, dirs, files in os.walk(data_dir):
        num_files = len(files)
        for i in range(num_files):
            with open(data_dir+files[i]) as f:
                data_json = json.load(f)

                mp_id = data_json["id"]
                data['id'] = mp_id

                # step 1: create BandsData class
                this_data = format_data.BandsData(mp_id=mp_id, crystal_system=crystal_system)

                bands = data_json["band"]["bands"]
                bands = np.array(bands)
                branches = data_json["band"]["branches"]
                number = data_json['number']
                spacegroup = data_json['spacegroup']

                # step 2: arrange data at hs points
                formatted_bands, new_dict = this_data.format_data(bands, branches)

                # step 3: do degeneracy translation
                if degeneracy:
                    translated_bands = this_data.degen_translate(formatted_bands,
                                                                 en_tolerance=en_tolerance)  # degeneracy translation
                else:
                    # if not padding:
                    translated_bands = formatted_bands
                    # else:
                    #    translated_bands = padded_bands

                # step 4: do bands padding
                if padding_b2t and padding_around_fermi:
                    print('>>>Note: \'padding_b2t\' and \'padding_around_fermi\' can not both be \'True\'')
                    print('>>> Default: do \'padding_b2t\' (padding from bottom to the top)')
                    padding_around_fermi = False

                if padding_b2t:
                    padded_bands = this_data.padding_b2t(translated_bands,
                                                         # padding_num=padding_num,
                                                         num_of_bands=num_of_bands)
                    padding = True
                elif padding_around_fermi:
                    fermi_index = this_data.find_fermi_index(formatted_bands)
                    # debugging
                    try:
                        padded_bands = this_data.padding_around_fermi(translated_bands,
                                                                      fermi_index=fermi_index,
                                                                      bands_below_fermi_limit=bands_below_fermi_limit,
                                                                      # padding_num=padding_num,
                                                                      num_of_bands=num_of_bands)
                    except Exception:
                        # print(">>>>>>>>>>mp-{}".format(mp_id))
                        pass
                    padding = True
                else:
                    padding = False

                # step 5: fix dimension of bands
                if around_fermi:
                    if not padding:
                        fermi_index = this_data.find_fermi_index(formatted_bands)  # locate fermi
                        new_bands = this_data.fix_bands_dim_around_fermi(translated_bands,
                                                                         num_of_bands=num_of_bands,
                                                                         fermi_index=fermi_index,
                                                                         bands_below_fermi_limit=bands_below_fermi_limit
                                                                         )
                    else:
                        print('>>>Note: \'padding\' and \'around_fermi\' can not both be \'True\'')
                        print('>>> Default: do \'padding\'')
                        new_bands = padded_bands
                else:
                    if b2t:
                        if not padding:
                            new_bands = this_data.fix_bands_dim_b2t(translated_bands)  # from bottom  to top
                        else:
                            print('>>>Note: \'padding\' and \'b2t\' can not both be \'True\'')
                            print('>>> Default: do \'padding\'')
                            new_bands = padded_bands
                    else:
                        if padding:
                            new_bands = padded_bands
                        else:
                            print('>>>Note: \'padding\',\'b2t\', \'around_fermi\' all received False')
                            print('>>>Doing nothing')
                            new_bands = None

                # step 6: save bands into files
                # Bands None exception

                if new_bands is None:
                    # print('\nThe fermi level is below {} for {} band'.format(bands_below_fermi_limit, mp_id))
                    low_fermi.append(mp_id)
                    # print('Continue...')
                    continue
                else:
                    data["bands"] = new_bands
                    # data["spacegroup"], data["number"] = get_space_group_from_file(mp_id)
                    data["spacegroup"], data["number"] = spacegroup, number

                    save_file_name = 'new_input_data_{}.json'.format(mp_id)

                    with open(save_dir+save_file_name, 'w') as file:
                        json.dump(data, file, cls=format_data.NumpyEncoder, indent=4)

                        print("\r\tFinished {}|Total: {}".format(count, num_files), end='')
                        count += 1

    print('\nThese are low fermi cases:\n {}'.format(low_fermi))

    print('Saving error file id...')
    with open('error_files.json', 'w') as ef:
        json.dump(error_files, ef, cls=format_data.NumpyEncoder, indent=2)
    print('Done, please check in {}'.format(save_dir))


def create_high_weights_new_data(data_dir, new_data_dir, lowest_weights_limit=100, greater=True, save=False, plt=True):
    print("Running... please wait")
    sg_num_list, total_num = diagnosis.check_specific_spacegroup_num(data_dir=data_dir,
                                                                     occurrence_limit=lowest_weights_limit,
                                                                     greater=greater,
                                                                     save=save, plt=plt)
    count = 0
    for i in sg_num_list:
        file_count = 0
        for subdir, dirs, files in os.walk(data_dir):
            num_files = len(files)
            for j in range(num_files):
                with open(data_dir + files[j]) as f:
                    data_json = json.load(f)

                    if data_json["number"] == i:
                        this_data = {}
                        this_data = data_json
                        this_data["new_number"] = count
                        with open(new_data_dir+files[j], 'w') as new_file:
                            json.dump(this_data, new_file, cls=format_data.NumpyEncoder, indent=2)
                        file_count +=1
                        print("\rSaved: {}".format(file_count), end="")

        count += 1
        print("\nFinished current spacegroup number, running next one: {}/{}".format(count, total_num))

    print("Done! Check in {}".format(new_data_dir))


def processing_2(data_dir='data/data/'):
    for i in range(7):
        crystal_system = i+1
        count = 0
        with open("data/guess/crystal_list_{}.txt".format(i + 1), "r") as list_file:
            for data_file_path in list_file:
                split = re.split('new_input', data_file_path)  # _data_<mp-id>.json
                data_name = 'raw'+split[1]
                # print(data_name)
                count += 1


if __name__ == "__main__":
    from config import args
    if args['create_data']['start']:
        cfg = args['create_data']
        create_new_data(data_dir=cfg['data_dir'],
                        degeneracy=cfg['degeneracy'],
                        en_tolerance=cfg['en_tolerance'],
                        padding_around_fermi=cfg['padding_around_fermi'],
                        padding_b2t=cfg['padding_b2t'],
                        around_fermi=cfg['around_fermi'],
                        b2t=cfg['b2t'],
                        num_of_bands=cfg['num_of_bands'],
                        bands_below_fermi_limit=cfg['bands_below_fermi_limit'],
                        save_dir=cfg['save_dir'])

    if args['create_hw_data']['start']:
        cfg2 = args['create_hw_data']
        create_high_weights_new_data(data_dir=cfg2['data_dir'],
                                     new_data_dir=cfg2['new_data_dir'],
                                     lowest_weights_limit=cfg2['lowest_weights_limit'])


