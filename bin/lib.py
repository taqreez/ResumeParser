"""
coding=utf-8
"""
import logging

import os
import pandas
import re
import yaml

CONFS = None

AVAILABLE_EXTENSIONS = {'.csv', '.doc', '.docx', '.eml', '.epub', '.gif', '.htm', '.html', '.jpeg', '.jpg', '.json',
                        '.log', '.mp3', '.msg', '.odt', '.ogg', '.pdf', '.png', '.pptx', '.ps', '.psv', '.rtf', '.tff',
                        '.tif', '.tiff', '.tsv', '.txt', '.wav', '.xls', '.xlsx'}


def load_confs(confs_path='../confs/config.yaml'):
    # TODO Docstring
    global CONFS

    if CONFS is None:
        try:
            CONFS = yaml.load(open(confs_path))
        except IOError:
            confs_template_path = confs_path + '.template'
            logging.warn(
                'Confs path: {} does not exist. Attempting to load confs template, '
                'from path: {}'.format(confs_path, confs_template_path))
            CONFS = yaml.load(open(confs_template_path))
    return CONFS


def get_conf(conf_name):
    return load_confs()[conf_name]


def archive_dataset_schemas(step_name, local_dict, global_dict):
    """
    Archive the schema for all available Pandas DataFrames
     - Determine which objects in namespace are Pandas DataFrames
     - Pull schema for all available Pandas DataFrames
     - Write schemas to file
    :param step_name: The name of the current operation (e.g. `extract`, `transform`, `model` or `load`
    :param local_dict: A dictionary containing mappings from variable name to objects. This is usually generated by
    calling `locals`
    :type local_dict: dict
    :param global_dict: A dictionary containing mappings from variable name to objects. This is usually generated by
    calling `globals`
    :type global_dict: dict
    :return: None
    :rtype: None
    """
    logging.info('Archiving data set schema(s) for step name: {}'.format(step_name))

    # Reference variables
    data_schema_dir = get_conf('data_schema_dir')
    schema_output_path = os.path.join(data_schema_dir, step_name + '.csv')
    schema_agg = list()

    env_variables = dict()
    env_variables.update(local_dict)
    env_variables.update(global_dict)

    # Filter down to Pandas DataFrames
    #data_sets = filter(lambda k,v: type(v) == pandas.DataFrame, env_variables.items())
    #data_sets = dict(data_sets)
    data_sets = {k: v for k, v in env_variables.items() if type(v) == pandas.DataFrame}

    for (data_set_name, data_set) in data_sets.items():
        # Extract variable names
        logging.info('Working data_set: {}'.format(data_set_name))

        local_schema_df = pandas.DataFrame(data_set.dtypes, columns=['type'])
        local_schema_df['data_set'] = data_set_name

        schema_agg.append(local_schema_df)

    # Aggregate schema list into one data frame
    agg_schema_df = pandas.concat(schema_agg)

    # Write to file
    agg_schema_df.to_csv(schema_output_path, index_label='variable')


def term_count(string_to_search, term):
    """
    A utility function which counts the number of times `term` occurs in `string_to_search`
    :param string_to_search: A string which may or may not contain the term.
    :type string_to_search: str
    :param term: The term to search for the number of occurrences for
    :type term: str
    :return: The number of times the `term` occurs in the `string_to_search`
    :rtype: int
    """
    try:
        regular_expression = re.compile(re.escape(term), re.IGNORECASE)
        result = re.findall(regular_expression, string_to_search)
        return len(result)
    except Exception as exception_instance:
        logging.error('Error occurred during regex search: {}'.format(exception_instance))
        return 0


def term_match(string_to_search, term):
    """
    A utility function which return the first match to the `regex_pattern` in the `string_to_search`
    :param string_to_search: A string which may or may not contain the term.
    :type string_to_search: str
    :param term: The term to search for the number of occurrences for
    :type term: str
    :return: The first match of the `regex_pattern` in the `string_to_search`
    :rtype: str
    """
    try:
        regular_expression = re.compile(term, re.IGNORECASE)
        result = re.findall(regular_expression, string_to_search)
        if len(result) > 0:
            return result[0]
        else:
            return None
    except Exception as exception_instance:
        logging.error('Error occurred during regex search: {}'.format(exception_instance))
        return None
