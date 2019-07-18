args = {
        'create_data':  # corresponding fn: load_data.create_new_data
        {
            'start': True,
            'data_dir': 'data/data/',
            'degeneracy': True,
            'en_tolerance': 0.001,
            'around_fermi': False,
            'b2t': False,
            'padding_b2t': False,
            'padding_around_fermi': True,
            'num_of_bands': 100,
            'bands_below_fermi_limit': 50,
            'save_dir': '../input_data_test01/'
            },

        'create_hw_data':   # corresponding fn: load_data.create_high_weights_new_data
        {
            'start': False,
            'data_dir': '../input_data_3/',
            'new_data_dir': '../hw_input_data_5_3/',
            'lowest_weights_limit': 100,
            'greater': False,
            'save': False,
            'plt': True
            }
        }