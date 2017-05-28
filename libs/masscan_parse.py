# encoding:utf-8
# code by evileo
'''
    Parses masscans xml output and writes it to a file
    in a prettier format
'''

import argparse
import logging
import xmltodict

def setup_logging(debug):
     '''
         Bootstraps the logging config and
         sets the correct logging level
         Arguments:
             debug (boolean) indicating if the verbosity
             of the script should be increased
     '''
     logger = logging.getLogger()
     handler = logging.StreamHandler()
     formatter = logging.Formatter(
             '%(asctime)s:%(levelname)s:%(message)s')
     handler.setFormatter(formatter)
     logger.addHandler(handler)

     if debug is True:
         logger.setLevel(logging.DEBUG)
     else:
         logger.setLevel(logging.INFO)


def parse_file(file_handle):
    '''
        Loads XML tags into a dict as keys, seting their
        values to the attribute of the tag
        Arguments:
            file_handle (file object) in read mode
        Returns:
            An ordered dictionary of parsed xml elements
    '''
    logging.info('Parsing XML file {}'.format(file_handle.name))
    parsed_file_data = xmltodict.parse(file_handle.read())
    return parsed_file_data


def write_output(file_handle, parsed_data):
    '''
        Formats the parsed XML data into a nicer format
        and writes it to a file
        Arguments:
            file_handle (file object) in write mode
            parsed_data (ordered dict) of xml elements and
            attributes
    '''
    logging.info('Formatting XML and writing to {}'.format(file_handle.name))
    for element in parsed_data['nmaprun']['host']:
        try:
            file_handle.write('IP: {}:{}\n'.format(element['address']['@addr'],
                    element['ports']['port']['@portid']))

            print 'IP: {}:{}\n'.format(element['address']['@addr'],
                    element['ports']['port']['@portid'])
            file_handle.write('State: {}\n'.format(element['ports']['port']['state']['@state']))
            file_handle.write('Banner: {}\n'.format(element['ports']['port']['service']['@banner']))
            file_handle.write('\n')
        except KeyError:
            file_handle.write('\n')
            continue


def main():
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument('-i',
            '--input',
            help='Input file to parse',
            type=argparse.FileType('r'),
            action='store',
            required=True)

    argument_parser.add_argument('-o',
            '--output',
            help='Output file to store results',
            type=argparse.FileType('w'),
            action='store',
            required=True)

    argument_parser.add_argument('-d',
            '--debug',
            help='Increase verbosity of script output',
            action='store_true')

    argument_list = argument_parser.parse_args()

    setup_logging(argument_list.debug)

    parsed_file_data = parse_file(argument_list.input)

    write_output(argument_list.output, parsed_file_data)


if __name__ == '__main__':
    main()