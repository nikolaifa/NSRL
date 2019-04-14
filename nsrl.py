
import logging
import json

log = logging.getLogger(__name__)






if __name__ == '__main__':
    ##########################################################################
    # local import
    ##########################################################################

    import argparse

    ##########################################################################
    # defined functions
    ##########################################################################

    nsrl_databases = [ 'file', 'os', 'manufacturer', 'product' ]

    def nsrl_create_database(**kwargs):
        database_type = kwargs['type']
        nsrl_databases[database_type].create_database(kwargs['database'],
                                                      kwargs['filename'])


    def readFromFile(**kwargs):
        database_type = kwargs['type']
        record = kwargs['filename']
        db_path = kwargs['database']wge
        print(database_type, " ", record, " ", db_path)
        from csv import DictReader

        csv_file = open(records, 'r')
        csv_entries = DictReader(csv_file)

        print(csv_entries[0]['SHA-1'])


    ##########################################################################
    # arguments
    ##########################################################################

    # define command line arguments
    desc_msg = 'NSRL database module CLI mode'
    parser = argparse.ArgumentParser(description=desc_msg)
    parser.add_argument('-v',
                        '--verbose',
                        action='count',
                        default=0)
    subparsers = parser.add_subparsers(help='sub-command help')

    # Create the database
    help_msg = 'create NSRL records into a database'
    create_parser = subparsers.add_parser('create',
                                          help=help_msg)
    create_parser.add_argument('-t',
                               '--type',
                               type=str,
                               choices=['file', 'os',
                                        'manufacturer', 'product'],
                               help='type of the record')
    create_parser.add_argument('filename',
                               type=str,
                               help='filename of the NSRL record')
    create_parser.add_argument('database',
                               type=str,
                               help='database to store NSRL records')
    create_parser.set_defaults(func=readFromFile)

    args = parser.parse_args()

    # set verbosity
    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    args = vars(parser.parse_args())
    func = args.pop('func')
    # with 'func' removed, args is now a kwargs
    # with only the specific arguments
    # for each subfunction useful for interactive mode.
    func(**args)