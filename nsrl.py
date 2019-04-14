
import logging
import json
import plyvel

log = logging.getLogger(__name__)



class NSRLCreate:
    key = None
    
    @classmethod
    def create_database(cls, dbfile, records, **kwargs):
        i = 0
        from csv import DictReader
        csv_file = open(records, 'r')
        csv_entries = DictReader(csv_file)

        db = plyvel.DB(dbfile, **kwargs, create_if_missing=True)
        try:
            for row in csv_entries:
                key = bytes(row.pop(cls.key), 'utf-8')
                value = db.get(key, None)
                row = json.dumps(row).encode('utf-8')

                if not value:
                    db.put(key, row)
            
                else:
                    db.delete(key)
                    print(value)
                    value = json.loads(value.decode('utf-8'))
                    print(value)
                    existing_entry = 
                    merged_entry = {key: value for (key, value) in (existing_entry.items() + row.items())}
                    print("existing: ", existing_entry)
                    print("row: ", row)
                    print(merged_entry)
                    break
        except UnicodeDecodeError:
            i += 1
        print(i)
# ==================
#  NSRL File Record
# ==================

class NSRLFile(NSRLCreate):

    key = "SHA-1"

# =================
#  NSRL OS Record
# =================

class NSRLOs(NSRLCreate):

    key = "OpSystemCode"

# ================
#  NSRL OS Record
# ================

class NSRLManufacturer(NSRLCreate):

    key = "MfgCode"

# =====================
#  NSRL Product Record
# =====================

class NSRLProduct(NSRLCreate):

    key = "ProductCode"


if __name__ == '__main__':
    ##########################################################################
    # local import
    ##########################################################################

    import argparse

    ##########################################################################
    # defined functions
    ##########################################################################

    nsrl_databases = {
        'file':         NSRLFile,
        'os':           NSRLOs,
        'manufacturer': NSRLManufacturer,
        'product':      NSRLProduct,
    }

    def nsrl_create_database(**kwargs):
        database_type = kwargs['type']
        nsrl_databases[database_type].create_database(kwargs['database'],
                                                      kwargs['filename'])


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
    create_parser.set_defaults(func=nsrl_create_database)

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