import argparse

from ASR_NL_benchmark import pipeline
from ASR_NL_benchmark import interface

if __name__ == "__main__":
    # Set parser
    parser = argparse.ArgumentParser(description='normalize ref and hyp file')
    parser.add_argument('-hyp', '--hypfile', nargs='+',
                        metavar=('hypfile_name', 'extension'),
                        default=['ASR_NL_benchmark/data/test_hyp.ctm', 'ctm'], help='help: path to the hypothesis file and its extension')
    parser.add_argument('-ref', '--reffile', nargs='+',
                        metavar=('reffile_name', 'extension'),
                        default=['ASR_NL_benchmark/data/test_ref.stm', 'stm'],
                        help='help: path to the reference file and its extension')
    parser.add_argument('-interactive',
                        metavar='value',
                        default='',
                        help='help: True if you want to use the GUI')

    args = parser.parse_args()

    if bool(args.interactive):
        print('Opening interface')
        interface.main()
    else:
        print('Running benchmarking')
        benchmarking = pipeline.Pipeline(args.hypfile[0], args.hypfile[1], args.reffile[0], args.reffile[1])
        benchmarking.main()
        pipeline.process_results()

