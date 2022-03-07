import great_expectations as ge
import logging
import json


def great_expectations_validation(data_path, file_format):
    """ Runs format validation on stm and ctm file
    ARGS:
        data_path: The path to the data
        file_format: The format to be checked (stm/ctm)
    """
    if file_format == 'stm':
        logging.info('Changed encoding to utf_8')
        stm_df = ge.read_csv(data_path, sep=' ', names=['file_name', 'waveform_channel',
                                                                  'speaker_id', 'begin_time', 'end_time',
                                                                  'label', 'text'],
                             header=None, comment=';')

        stm_df.expect_column_values_to_be_of_type('text', 'str', meta={
            "notes": "Make sure the last column is a string type"
        })
        stm_df.expect_column_values_to_be_of_type('label', 'str', meta={
            "notes": "The label should be a string type"
        })
        stm_df.expect_column_values_to_be_of_type('end_time', 'float', meta={
            "notes": "The fifth column should denote the end time, make sure the third column is a float type"
        })
        stm_df.expect_column_values_to_be_of_type('begin_time', 'float', meta={
            "notes": "The fourth column should denote the begin time, make sure the type is float"
        })
        stm_df.expect_column_values_to_be_of_type('speaker_id', 'str', meta={
            "notes": "The third column should be the speaker id , make sure the column is string type"
        })

        stm_df.expect_column_values_to_be_of_type('file_name', 'str', meta={
            "notes": "The first column should be the waveform filename, make sure the column is string type"
        })

        with open("/input/ref_expectation_file.json", "w") as my_file:
            my_file.write(
                json.dumps(stm_df.get_expectation_suite().to_json_dict())
            )

        return True

    if file_format == 'ctm':
        ctm_df = ge.read_csv(data_path, sep=' ', names=['file_name', 'waveform_channel',
                                                                  'begin_time', 'duration', 'text',
                                                                  'confidence'],
                             header=None, comment=';')

        ctm_df.expect_column_values_to_be_between(
            'confidence', min_value=0, max_value=1,
            meta={
                "notes": "Make sure last column (confidence) is always between 0 and 1"
            })

        ctm_df.expect_column_values_to_be_of_type('text', 'str', meta={
            "notes": "Make sure the last column is a string type"
        })

        ctm_df.expect_column_values_to_be_of_type('text', 'str', meta={
            "notes": "Make sure the last column is a string type"
        })

        ctm_df.expect_column_values_to_be_of_type('duration', 'float', meta={
            "notes": "The fifth column should denote the end time, make sure the third column is a float type"
        })

        ctm_df.expect_column_values_to_be_of_type('file_name', 'str', meta={
            "notes": "The first column should be the waveform filename, make sure the column is string type"
        })

        with open("/input/hyp_expectation_file.json", "w") as my_file:
            my_file.write(
                json.dumps(ctm_df.get_expectation_suite().to_json_dict())
            )

        return True
