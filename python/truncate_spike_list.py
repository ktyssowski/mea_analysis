import itertools as it
from argparse import ArgumentParser
from os import path
from shutil import copyfile

def configure_parser():
    parser = ArgumentParser(
        description='Removes trailing information from the end of a csv file that invalidates it for normal parsing'
    )
    parser.add_argument('file_paths', type=path.expanduser, nargs='+',
        help='Path(s) to the csv files to process'
    )
    parser.add_argument('-b', '--no_backup', action='store_true', 
        help='Creates a backup of the original file at the original filepath with the .bk extension (i.e. sample.csv.bk)'
    )
        
    return parser

def back_up_files(file_paths):
    create_bk_path = lambda p: p + '.bk'
    bk_paths = map(create_bk_path, file_paths)
    for fp, bkfp in it.izip(file_paths, bk_paths):
        copyfile(fp, bkfp)

def truncate_file_contents(file_contents):
    split_contents = file_contents.split('\r\n')
    try:
        # Search for the first null line. Add one so that it will be included when we piece
        #  the file back together
        truncate_ind = split_contents.index('') + 1
    except ValueError:
        # This will fail if the null line cannot be found. Do nothing in this case
        return file_contents
    finally:
        # If the truncate_ind is found, join the contents leading up to the first null line
        return '\r\n'.join(split_contents[:truncate_ind])

def main():
    parser = configure_parser()
    args = parser.parse_args()

    # Back up the files if the user doesn't say not to.
    #  the double negative makes the code confusing but the commands make more sense
    if not args.no_backup:
        back_up_files(args.file_paths)

    csv_files = it.imap(open, args.file_paths)
    csv_contents = it.imap(file.read, csv_files)
    truncated_contents = it.imap(truncate_file_contents, csv_contents)

    for output_string, output_path in it.izip(truncated_contents, args.file_paths):
        output_file = open(output_path, 'w')
        output_file.write(output_string)
        output_file.close()

if __name__ == '__main__':
    main()
