from argparse import ArgumentParser
from os import path

DEFAULT_NUM_LINES = 4e6

def configure_parser():
    parser = ArgumentParser(
        description='Splits an input csv file into multiple, smaller, output files'
    )
    parser.add_argument(
        'input_file', type=path.expanduser, help='Path to the input file to split'
    )
    parser.add_argument(
        '-l', '--num_lines', type=int, default=DEFAULT_NUM_LINES,
        help='Number of lines to add to each output file. Default = %d' % DEFAULT_NUM_LINES
    )
    return parser

def main():
    parser = configure_parser()
    args = parser.parse_args()
    input_file = open(args.input_file)
    header = input_file.readline()

    output_file = None # place holder, for initializing
    for i, l in enumerate(input_file):
        if i % args.num_lines == 0:
            if output_file is not None:
                # Close the open output_file if it exists
                output_file.close()
            output_file_no = '_%03d' % (i/args.num_lines)
            output_path = path.splitext(args.input_file)[0] + output_file_no + '.csv'
            output_file = open(output_path, 'w')
            output_file.write(header)

        output_file.write(l)

    output_file.close()

if __name__ == '__main__':
    main()
