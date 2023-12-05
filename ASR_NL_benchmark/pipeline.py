"""The main module of the dutch ASR-Benchmarking tool"""
from datetime import date
import os
import logging
import glob
import pandas

from ASR_NL_benchmark.normalize import replace_numbers_and_symbols
from ASR_NL_benchmark.validate import great_expectations_validation
from ASR_NL_benchmark.input_classes import STM, CTM


def set_logging(logpath):
    """ Sets logging
    Args:
        logpath: the place where the log file wil be placed
    Returns:
        logging: the configured logger
    """
    if not os.path.isfile(logpath):
        with open(logpath, 'a+') as file:
            file.write('Start Logging')

    logging.basicConfig(filename=logpath, level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    return logging


def run_pipeline(hypfile, reffile, skip_ref_norm, skip_hyp_norm):
    """ Validates and Normalizes the hyp and ref file and runs them trough sclite
    Args:
        hypfile: the hypothesis file
        reffile: the refference file
    """
    # Validate
    hypfile.validate(great_expectations_validation)
    reffile.validate(great_expectations_validation)

    # Normalize
    if not skip_ref_norm:
        reffile.clean_text(replace_numbers_and_symbols)
    reffile.export(os.path.join(os.path.sep,'input',f'{reffile.name}_normalized.{reffile.extension}'))
    if not skip_hyp_norm:
        hypfile.clean_text(replace_numbers_and_symbols)
    hypfile.export(os.path.join(os.path.sep,'input',f'{hypfile.name}_normalized.{hypfile.extension}'))

    #Create results folder if not exists:
    if not os.path.exists(os.path.join(os.path.sep,'input','results')):
        os.makedirs(os.path.join(os.path.sep,'input','results'))

    # Run variation scripts
    logging.info(
        f"running: sclite -h {hypfile.normalized_path} {hypfile.extension} -r {reffile.normalized_path} {reffile.extension} -m hyp -O {os.path.join(os.path.sep,'input','results')}  -o dtl spk")
    run = os.system(
        f"csrfilt.sh -s -i ctm {os.path.join('ASR_NL_benchmark','variations.glm')} < {hypfile.normalized_path} > {hypfile.variation_path}")

    # Run sclite
    run = os.system(
        f"csrfilt.sh -s -i stm {os.path.join('ASR_NL_benchmark','variations.glm')} < {reffile.normalized_path} > {reffile.variation_path}")
    run = os.system(
        f"sclite -D -h {hypfile.variation_path} {hypfile.extension} -r {reffile.variation_path} {reffile.extension} -O {os.path.join(os.path.sep,'input','results')} -o dtl spk")

def calculate_wer(df):
    """ Calculates the word error rate and adds the collumn 'product' to the dataframe
    Args:
        df: a Pandas Dataframe to calculate used to calculate the wer
    Returns:
        df: The pandas dataframe with the column: 'product' (the product of the word error rate and the amount of ref words
        wer: The word error rate

    >>> DUMMY_DF = pandas.DataFrame({'wer':[0.2,0.4,0.1],'ref_words':[10,2,5]})
    >>> calculate_wer(DUMMY_DF)
    (   wer  ref_words  product
    0  0.2         10      2.0
    1  0.4          2      0.8
    2  0.1          5      0.5, 0.1941176470588235)

    """
    df['product'] = df['wer'] * df['ref_words']
    wer = float(df['product'].sum()) / float(df['ref_words'].sum())
    return df, wer

def calculate_wer_per_cat(df,category='category', id='', kind=''):
    """ Calculates the WER for every unique value for a certain column
    Args:
        df: the pandas dataframe
        category: name of a column in the pandas data frame, for each unique in this column value we return the wer.
        kind: name of the asr-tool
    Returns:
        df_out: a pandas dataframe with the word error rates for each value in the category
    >>> from minimock import mock
    >>> mock('pandas.DataFrame.to_csv')
    >>> DUMMY_DF = pandas.DataFrame({'wer':[0.2,0.4,0.1],'ref_words':[10,2,5], 'product':[2,0.8,0.5],'category':['aap','banaan','aap']})
    >>> calculate_wer_per_cat(DUMMY_DF)
    Called pandas.DataFrame.to_csv(
        '\\\\input\\\\results\\\\results_category_.csv',
        index=False)
      category  ref_words   WER   kind
    0      aap         15  0.17  False
    1   banaan          2  0.40  False

    """
    df_out = df.groupby(category, as_index=False).agg({'ref_words': 'sum', 'product': 'sum'})
    df_out['WER'] = (df_out['product'] / df_out['ref_words']).round(2)
    df_out = df_out.drop('product', 1)
    df_out['kind'] = kind
    df_out.to_csv(os.path.join(os.path.sep, 'input', 'results', f'results_{category}_{id}_{kind}.csv'), index=False)
    return df_out

def process_results_dtl_only(path_parts=('input','results'), id='', kind= False):
    """ Processes the results
    Args:
        path_parts: The parts of the path to the results
        id: identifier
        kind: name of the asr-tool
    Returns:
        wer: Returns the word error rate
        df_2: A pandas dataframe with the word error rates per category
    """
    path = os.path.join(os.path.sep, *path_parts, '')
    print('Processing results')
    df = pandas.DataFrame(columns=['wer', 'ref_words', 'category'])
    for name in glob.glob(f'{path}*.dtl'):
        category = os.path.basename(name).split('-')[-1].split('.')[0][:-22]
        with open(name,'r') as file:
            line_list = file.read().split('\n')
            for line in line_list:
                if line.startswith('Percent Total Error'):
                    for item in line.split(' '):
                        if '%' in item:
                            wer = float(item[:-1])
                elif line.startswith('Ref. words'):
                    ref_words = float(line.split(' ')[-1].replace('(','').replace(')',''))

        df.loc[os.path.basename(name)] = [float(wer), int(ref_words), str(category)]
    df, wer = calculate_wer(df)
    df_2 = calculate_wer_per_cat(df, 'category', id, kind)
    return wer, df_2



def process_results(path_parts= ('input','results'), id='', kind=False):
    """ Processes the results
    Args:
        path_parts: The parts of the path to the results
        id: identifier
        kind: name of the asr-tool
    Returns:
        wer: Returns the word error rate
        df_2: A pandas dataframe with the word error rates per category
    """
    path = os.path.join(os.path.sep, *path_parts, '')
    print('Processing results on speaker level')
    df = pandas.DataFrame(columns=['wer', 'ref_words', 'category', 'speaker'])
    for name in glob.glob(f'{path}*.spk.*'):
        category = os.path.basename(name).split('-')[-1].split('.')[0][:-22]
        speaker = os.path.splitext(name)[-1]
        with open(name,'r') as file:
            line_list = file.read().split('\n')
            for line in line_list:
                if line.startswith('Percent Total Error'):
                    for item in line.split(' '):
                        if '%' in item:
                            if item[:-1] != 'UNDEF':
                                wer = float(item[:-1])
                            else:
                                wer = False
                elif line.startswith('Ref. words'):
                    ref_words = float(line.split(' ')[-1].replace('(', '').replace(')', ''))
        if wer:
            df.loc[os.path.basename(name)] = [float(wer), int(ref_words), str(category), str(speaker)]
    try:
        df, wer = calculate_wer(df)
        df_2 = calculate_wer_per_cat(df,category='category', id=id, kind=kind)

    except ZeroDivisionError:
        df = df[df.ref_words != 0]
        df_missing_ref = df[df.ref_words == 0]
        print(f"No reference words found for:")
        print(df_missing_ref)
        df, wer = calculate_wer(df)
        df_2 = calculate_wer_per_cat(df, category='category', id=id, kind=kind)

    df_3 = calculate_wer_per_cat(df, category ='speaker', id=id, kind =kind)

    return wer, df_2, df_3


def process_input(hypfile_arg, reffile_arg):
    """ Processes the input arguments
    Args:
        hypfile_arg: the hypfile arguments entered by the user
        reffile_arg: the reffile arguments entered by the user
    Returns:
        hyp_list: A list with all hypothesis file paths
        ref_list: A list with all reference file paths
    """
    # check input are files or dirs:
    ref_is_dir = os.path.isdir(reffile_arg)
    hyp_is_dir = os.path.isdir(hypfile_arg)
    if ref_is_dir:
        assert hyp_is_dir
        ref_list = [os.path.join(reffile_arg,x) for x in os.listdir(reffile_arg)]
        hyp_list = [os.path.join(hypfile_arg,x) for x in os.listdir(hypfile_arg)]
        assert len(ref_list) == len(hyp_list)

    else:
        hyp_list = [hypfile_arg]
        ref_list = [reffile_arg]

    return hyp_list, ref_list


class Pipeline():
    def __init__(self, hypfile_input_path, hypextension, reffile_input_path, refextension, kind, skip_ref_norm, skip_hyp_norm):
        self.progress = 0
        self.failed = 0
        self.hypfile_input_path = os.path.join(os.path.sep,'input',hypfile_input_path)
        self.reffile_input_path = os.path.join(os.path.sep,'input',reffile_input_path)
        self.hypextension = hypextension
        self.refextension = refextension
        self.kind = kind
        self.skip_ref_norm = skip_ref_norm
        self.skip_hyp_norm = skip_hyp_norm
        self.logging = set_logging(logpath=os.path.join(os.path.sep,'input',f'{date.today()}_logging.log'))
        self.logging.info(f"hypfile path from terminal: {hypfile_input_path}")
        self.logging.info(f"reffile path from terminal: {reffile_input_path}")
        self.logging.info(f"Pipeline class' hypfile path: {self.hypfile_input_path}")
        self.logging.info(f"Pipeline class' reffile path: {self.reffile_input_path}")
        self.logging.info(f"Skip reffile normalization: {self.skip_ref_norm}")
        self.logging.info(f"Skip hypfile normalization: {self.skip_hyp_norm}")

    def main(self):
        hyp_list, ref_list = process_input(self.hypfile_input_path, self.reffile_input_path)
        done = 0
        total = len(hyp_list)
        for hypfile_path, reffile_path in zip(hyp_list, ref_list):
            try:
                print(f'start {done+1} / {total}')
                print(f'start comparing {hypfile_path} to {reffile_path}')
                # Parse input
                reffile = STM(reffile_path, self.refextension)
                hypfile = CTM(hypfile_path, self.hypextension)
                run_pipeline(hypfile, reffile, self.skip_ref_norm, self.skip_hyp_norm)
                done += 1
                self.progress = done/total
            except:
                print(f"failed {hypfile_path} - {reffile_path}")
                done +=1
                self.progress = done/total
                self.failed += 1
        process_results(path_parts=('input','results'), kind=self.kind)












