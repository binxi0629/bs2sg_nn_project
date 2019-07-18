from pymatgen.ext.matproj import MPRester
from diagnosis import diagnosis
import format_data
import json, os, re
import numpy as np


def create_cs_data(data_name,
                   crystal_system,
                   data_dir='../data/',
                   degeneracy=False,
                   en_tolerance=0.01,
                   around_fermi=False,
                   b2t=False,
                   padding_b2t=False,
                   padding_around_fermi=False,
                   # padding_num=9999,
                   num_of_bands=30,
                   bands_below_fermi_limit=15):
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
    num_data = 1
    save_dir = 'data/cs_data/cs_{}_input_data/'.format(crystal_system)

    split = re.split('raw', data_name)
    # print(split)

    with open(data_dir + data_name) as f:
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
                print(">>>>>>>>>>mp-{}".format(mp_id))

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
            print('Bands is None: {}'.format(data_name))
        else:
            data["bands"] = new_bands
            # data["spacegroup"], data["number"] = get_space_group_from_file(mp_id)
            data["spacegroup"], data["number"] = spacegroup, number

            save_file_name = 'new_input{}'.format(split[1])

            with open(save_dir + save_file_name, 'w') as file:
                json.dump(data, file, cls=format_data.NumpyEncoder, indent=4)


def processing_2(data_dir='data/data/'):
    print('Data processing...')
    for i in range(7):
        crystal_system = i+1
        crystal_system = str(crystal_system)
        count = 0
        with open("data/guess/crystal_list_{}.txt".format(i + 1), "r") as list_file:
            for data_file_path in list_file:
                split_name = re.split('\n', data_file_path)
                split_name = re.split('new_input', split_name[0])  # _data_<mp-id>.json
                data_name = 'raw'+split_name[1]
                # print(data_name)
                count += 1

                create_cs_data(data_dir=data_dir,
                               data_name=data_name,
                               crystal_system=crystal_system,
                               degeneracy=True,
                               en_tolerance=0.001,
                               around_fermi=False,
                               b2t=False,
                               padding_b2t=True,
                               padding_around_fermi=False,
                               # padding_num=9999,
                               num_of_bands=100,
                               bands_below_fermi_limit=50)
                print('\rCrystal System: {cs}| Finished: {num_data}'.format(cs=crystal_system,
                      num_data=count),
                      end='')
        print('\rCrystal System: {cs}| Total: {num_data}'.format(cs=crystal_system,
              num_data=count))
    print('Finished crystal system data processing')
    print('Running Neural Network...')


def rm_all_files_in_cs_input_data():
    import shutil
    for i in range(7):
        shutil.rmtree(f'data/cs_data/cs_{i + 1}_input_data/')
        os.mkdir(f'data/cs_data/cs_{i + 1}_input_data/')


if __name__ == '__main__':
    rm_all_files_in_cs_input_data()
    processing_2(data_dir='data/data/')   # <<<<<
    pass
