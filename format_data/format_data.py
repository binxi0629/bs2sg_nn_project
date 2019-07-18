import json
import re
import numpy as np
import shutil
import os


class BandsData:

    def __init__(self, mp_id, crystal_system='0', *args):

        # generic dict of high-symmetry points
        self.__gen_dict = {
            '\\Gamma': None,  # Center of the Brillouin zone
            'M': None,  # Center of an edge
            'R': None,  # Corner point
            'X': None,  # Center of a face
            'K': None,  # Middle of an edge joining two hexagonal faces
            'L': None,  # Center of a hexagonal face
            'U': None,  # Middle of an edge joining a hexagonal and a square face
            'W': None,  # Corner point
            'H': None,  # Corner point joining four edges
            'N': None,  # Center of a face
            'P': None,  # Corner point joining three edges
            'A': None,  # Center of a hexagonal face
        }

        # self.file_name = file_name
        self.mp_id = mp_id
        self.cs = crystal_system

        # read dict from file
        if self.cs == '0':
            self.this_dict = self.__gen_dict
        else:
            with open('CS_dict.json', 'r') as file:
                cs_dict = json.load(file)
                self.this_dict = cs_dict[self.cs]

    @staticmethod
    def load_data(file_dir='../data/', mp_id='mp_id'):
        """
            This is used to load data from downloaded data file, each .json data file contains original bands matrix,
            and their corresponding high-symmetry direction e.g. '\\Gamma-X'

        :param file_dir: dir of .json file, default: '../data/'
        :param mp_id: material-project id
        :return: bands: bands info in matrix form
                branches: contains info of bands along which high-symmetry direction

        """

        with open('{file_dir}raw_data_{mp_id}.json'.format(file_dir=file_dir, mp_id=mp_id), 'r') as f:
            data = json.load(f)
            bands = data["band"]["bands"]
            bands = np.array(bands)
            branches = data["band"]["branches"]

        return bands, branches

    def format_data(self, bands, branches):
        """
            This is for formatting original data

        :param bands: bands info in matrix form
        :param branches: contains info of bands along which high-symmetry direction
        :return: formatted_bands: formatted bands info in matrix form
                 self.this_dict: write the split high-symmetry points, in dict form

        """
        # self.this_dict = self.__gen_dict
        order = []  # list to store high-symmetry point
        band_index = {}  # dict to store band index info corresponding to its high-symmetry point e.g. "X": 18
        formatted_bands = []
        zero_matrix = np.zeros(np.shape(bands))
        """
            zero_matrix is for: if one configuration does not have some high-symmetry points listed in __generic_dict
            then fill zeros in those columns 
        """

        for i in range(len(branches)):
            order.append(branches[i]["name"])
            spilt = re.split('-', order[i])

            band_index[spilt[0]] = branches[i]['start_index']
            band_index[spilt[1]] = branches[i]['end_index']

        # print('>>>>>>>>>>>>>>>>>>', band_index)
        # iterate all keys in band_index, and if exists, give value to this_dict, if not, pass
        for hs_point in band_index:
            if hs_point in self.this_dict:
                self.this_dict[hs_point] = band_index[hs_point]
        # print('>>>>>>>>>>>>>>>>>', BandsData.__gen_dict)

        # iterate all keys in this_dict, export bands (not arranged in bands dimension)
        for hs_point in self.this_dict:
            hs_value = self.this_dict[hs_point]
            if self.this_dict[hs_point] is None:
                # fill zeros in bands
                formatted_bands.append(zero_matrix[:, 0])
            else:
                formatted_bands.append(bands[:, hs_value])

        # transpose of formatted_bands
        formatted_bands = np.transpose(formatted_bands)

        return formatted_bands, self.this_dict

    @staticmethod
    def degen_translate(formatted_bands, en_tolerance=0.01):
        """
            This method is for represent the bands matrix into a degeneracy form
        :param formatted_bands: one of the output from format_data() method
        :param en_tolerance: energy tolerance, default 0.01eV
        :return:
        """
        tmp = np.array(formatted_bands)
        size = np.shape(tmp)

        degen_bands = np.zeros(size)  # assumption 1: missing data are assumed null, labeled by 0
        # degen_bands = np.zeros(size)+1  # assumption 2: missing data are assumed non-degenerate, labeled by 1

        # Need further test
        for i in range(size[1]):
            each_column = []
            count = 1
            for j in range(size[0]-1):
                if tmp[j][i] == 0:
                    count = 0
                    break
                else:
                    if np.absolute(tmp[j+1][i]-tmp[j][i]) <= en_tolerance:
                        count += 1
                    else:
                        for k in range(count):
                            each_column.append(count)
                        count = 1

            if count == 0:
                pass
            else:
                for k in range(count):
                    each_column.append(count)
                degen_bands[:, i] = np.array(each_column)

        return degen_bands

    @staticmethod
    def fix_bands_dim_b2t(degen_bands, num_of_bands=30):
        """
            This method is for cut bands dimension to a fixed number, default 30
        :param degen_bands: output from degen_translate() method
        :param num_of_bands: the fixed dimension default:30 (30 is the minimum bands value of all data)
        :return: fixed_bands_num: bands matrix with fixed dimension
        """

        tmp = np.array(degen_bands)

        # A filter: bands dimension must larger than num_of_bands
        fixed_bands = tmp[0:num_of_bands, :]
        # print(np.shape(fixed_bands))
        return fixed_bands

    @staticmethod
    def find_fermi_index(formatted_bands):
        tmp = np.array(formatted_bands)
        # count bands number
        bands_num = np.shape(tmp)[0]

        for j in range(bands_num):
            if (tmp[j][0]) * (tmp[j + 1][0]) <= 0:
                fermi_index = j
                # print(j)
                return fermi_index

        print('Error: fermi_index not found')

    def vb_count(self, formatted_bands, fermi_index=0):
        return fermi_index + 1

    def cb_count(self, formatted_bands, fermi_index=0):
        tmp = np.array(formatted_bands)
        bands_num = np.shape(tmp)[0]
        return bands_num-fermi_index-1

    def padding_judgement(self,
                          conduction_num,
                          valence_num,
                          bands_below_fermi_limit):

        if valence_num < bands_below_fermi_limit:
            padding_btm = True
        else:
            padding_btm = False

        if conduction_num < bands_below_fermi_limit:
            padding_top = True
        else:
            padding_top = False

        return padding_btm, padding_top

    @staticmethod
    def fix_bands_dim_around_fermi(degen_bands, bands_below_fermi_limit=15, num_of_bands=30, fermi_index=0):
        tmp = np.array(degen_bands)

        # judge if fermi_index <= bands_below_fermi_limit
        if fermi_index <= (bands_below_fermi_limit-1):
            # bands_around_fermi = tmp[0:num_of_bands, :]
            return None
        else:
            start_index = fermi_index-bands_below_fermi_limit
            end_index = start_index+num_of_bands
            bands_around_fermi = tmp[start_index:end_index, :]

            return bands_around_fermi

    def padding_b2t(self,
                    formatted_bands,
                    # padding_num=9999,
                    num_of_bands=100):

        padding_num = 0  # <<< all padding number should be zero
        # bands padding from bottom to the top
        tmp = np.array(formatted_bands)
        bands_num = np.shape(tmp)[0]
        row_dim = len(self.this_dict)

        padding_vector = []
        [padding_vector.append(padding_num) for num in range(row_dim)]

        if bands_num > num_of_bands:
            padded_bands = self.__class__.fix_bands_dim_b2t(formatted_bands, num_of_bands=num_of_bands)
            # print('larger: {}'.format(len(padded_bands)))
        else:
            count = num_of_bands-bands_num
            for i in range(count):
                tmp = np.append(tmp, [padding_vector], axis=0)
            padded_bands = tmp
            # print('padded: {}'.format(len(padded_bands)))

        return padded_bands

    def padding_around_fermi(self,
                             formatted_bands,
                             num_of_bands,
                             bands_below_fermi_limit,
                             # padding_num=9999,
                             fermi_index=0):
        padding_num = 0  # <<< all padding number should be zero

        # bands padding around fermi level
        tmp = np.array(formatted_bands)
        bands_num = np.shape(tmp)[0]
        row_dim = len(self.this_dict)

        padding_vector = []
        [padding_vector.append(padding_num) for num in range(row_dim)]

        conduction_bands_num = self.cb_count(formatted_bands, fermi_index=fermi_index)
        # print(conduction_bands_num)
        valence_bands_num = self.vb_count(formatted_bands, fermi_index=fermi_index)
        # print(valence_bands_num)
        padding_btm, padding_top = self.padding_judgement(conduction_bands_num,
                                                          valence_bands_num,
                                                          bands_below_fermi_limit=bands_below_fermi_limit)

        valence_bands = tmp[0:fermi_index+1, :]
        if not padding_btm:
            btm_bands = tmp[fermi_index-bands_below_fermi_limit:fermi_index, :]
        else:
            padded_btm_bands = []
            btm_num = bands_below_fermi_limit-valence_bands_num
            [padded_btm_bands.append(padding_vector) for num in range(btm_num)]
            padded_btm_bands = np.array(padded_btm_bands)
            btm_bands = np.concatenate((padded_btm_bands, valence_bands), axis=0)
            # print('btm_bands_num', len(btm_bands))
            # print('padded_bands_num', len(padded_btm_bands))
            # print('vb_num', len(valence_bands))

        conduction_bands = tmp[fermi_index+1:, :]
        if not padding_top:
            top_bands = tmp[fermi_index+1:fermi_index+bands_below_fermi_limit+1, :]
        else:
            padded_top_bands = []
            top_num = bands_below_fermi_limit-conduction_bands_num
            [padded_top_bands.append(padding_vector) for num in range(top_num)]
            padded_top_bands = np.array(padded_top_bands)
            top_bands = np.concatenate((conduction_bands, padded_top_bands), axis=0)
            # print('top_bands_num', len(top_bands))
            # print('padded_bands_num', len(padded_top_bands))
            # print('cb_num', len(conduction_bands))

        padded_bands = np.concatenate((btm_bands, top_bands), axis=0)

        # print(len(padded_bands))
        if len(padded_bands) != num_of_bands:
            raise Exception("Bands number not 100")

        return padded_bands


class NumpyEncoder(json.JSONEncoder):
    """
        to solve Error: NumPy array is not JSON serializable
        see: https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
