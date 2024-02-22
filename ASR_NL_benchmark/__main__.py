import argparse

from ASR_NL_benchmark import pipeline
from ASR_NL_benchmark import interface

if __name__ == "__main__":
    # Set parser
    parser = argparse.ArgumentParser(description='normalize ref and hyp file')
    parser.add_argument('-hyp', '--hypfile', nargs=2,
                        metavar=('hypfile_name', 'extension'),
                        default=['ASR_NL_benchmark/data/test_hyp.ctm', 'ctm'],
                        help='path to the hypothesis file and its extension')
    parser.add_argument('-ref', '--reffile', nargs=2,
                        metavar=('reffile_name', 'extension'),
                        default=['ASR_NL_benchmark/data/test_ref.stm', 'stm'],
                        help='path to the reference file and its extension')
    parser.add_argument('-kind', '--kind',
                        metavar=('speechrecognizer'),
                        default='',
                        help='enter the name of your speech recognizer')
    parser.add_argument('-interactive',
                        action = 'store_true',
                        help='if you want to use the GUI')
    parser.add_argument('-skip_ref_normalization', 
                        action = 'store_true',
                        help = 'skip the normalization step for the reference file')
    parser.add_argument('-skip_hyp_normalization', 
                        action = 'store_true',
                        help = 'skip the normalization step for the hypothesis file')

    args = parser.parse_args()

    if args.interactive:
        print('Opening interface')
        interface.main()
    else:
        print('Running benchmarking')
        benchmarking = pipeline.Pipeline(args.hypfile[0], args.hypfile[1], \
                                         args.reffile[0], args.reffile[1], \
                                         kind=args.kind, \
                                         skip_ref_norm=args.skip_ref_normalization, skip_hyp_norm=args.skip_hyp_normalization)
        benchmarking.main()
        pipeline.process_results(kind=args.kind)

