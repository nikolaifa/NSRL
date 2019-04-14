
import logging
import json
import plyvel

log = logging.getLogger(__name__)

class NSRL(object):

    def __init__(self,
                 nsrl_file,
                 nsrl_product,
                 nsrl_os, nsrl_manufacturer,
                 **kwargs):
        # TODO: need to specify paths in constructor,
        # temporary pass via kwargs
        self.nsrl_file = NSRLFile(nsrl_file)
        self.nsrl_product = NSRLProduct(nsrl_product)
        self.nsrl_os = NSRLOS(nsrl_os)
        self.nsrl_manufacturer = NSRLManufacturer(nsrl_manufacturer)

    def lookup_by_sha1(self, sha1sum):
        operations = [
            (sha1sum, 'SHA-1', self.nsrl_file, None),
            (None, 'ProductCode', self.nsrl_product, 'SHA-1'),
            (None, 'OpSystemCode', self.nsrl_os, 'SHA-1'),
            (None, 'MfgCode', self.nsrl_manufacturer, 'ProductCode')
        ]
        entries = dict((name, {}) for (_, name, _, _) in operations)

        for value, key, database, where in operations:
            if value:
                entries[key][value] = database.get(bytes(value))
            else:
                subkeys = set()
                for subkey, subitem in list(entries[where].items()):
                    if not isinstance(subitem, list):
                        subitem = [subitem]
                    subkeys.update([x[key] for x in subitem])
                for subkey in subkeys:
                    entries[key][subkey] = database.get(bytes(subkey))

        return entries


class NSRLCreate:
    key = None
    db = None

    def __init__(self, db, records, **kwargs):
        db = plyvel.DB(db, **kwargs, create_if_missing=True)

    def get(self, db_key):
        return db.get(bytes(db_key))
    
    @classmethod
    def create_database(cls, dbfile, records, **kwargs):
        i = 0
        from csv import DictReader
        csv_file = open(records, 'r')
        csv_entries = DictReader(csv_file)

        if not db:
            db = plyvel.DB(db, **kwargs, create_if_missing=True)

        try:
            for row in csv_entries:
                key = bytes(row.pop(cls.key), 'utf-8')
                value = db.get(key, None)
                
                if not value:
                    row = json.dumps(row).encode('utf-8')
                    db.put(key, row)
            
                else:
                    db.delete(key)
                    existing_entry = json.loads(value.decode('utf-8'))
                    row = { key: value for (key, value) in dict(list(existing_entry.items()) + list(row.items())).items() }
                    row = json.dumps(row).encode('utf-8')
                    db.put(key, row)

        except UnicodeDecodeError:
            i += 1
        print("Number of non-unicode hex: ", i)

# ==================
#  NSRL File Record
# ==================

class NSRLFile(NSRLCreate):

    key = "SHA-1"
    def __init__(self, db, **kwargs):
        # give default_dir value somewhere
        super(NSRLFile, self).__init__(db, 'NSRLFile.txt', **kwargs)

# =================
#  NSRL OS Record
# =================

class NSRLOS(NSRLCreate):

    key = "OpSystemCode"
    def __init__(self, db, **kwargs):
        # give default_dir value somewhere
        super(NSRLOS, self).__init__(db, 'NSRLOS.txt', **kwargs)

# ================
#  NSRL OS Record
# ================

class NSRLManufacturer(NSRLCreate):

    key = "MfgCode"
    def __init__(self, db, **kwargs):
        # give default_dir value somewhere
        super(NSRLManufacturer, self).__init__(db, 'NSRLMfg.txt', **kwargs)

# =====================
#  NSRL Product Record
# =====================

class NSRLProduct(NSRLCreate):

    key = "ProductCode"
    def __init__(self, db, **kwargs):
        # give default_dir value somewhere
        super(NSRLProduct, self).__init__(db, 'NSRLProd.txt', **kwargs)


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
        'os':           NSRLOS,
        'manufacturer': NSRLManufacturer,
        'product':      NSRLProduct,
    }

    def nsrl_create_database(**kwargs):
        database_type = kwargs['type']
        nsrl_databases[database_type].create_database(kwargs['database'],
                                                      kwargs['filename'])

    def nsrl_get(**kwargs):
        database_type = kwargs['type']
        database = nsrl_databases[database_type](kwargs['database'])
        value = database.get(bytes(kwargs['key']))
        print(("key {0}: value {1}".format(kwargs['key'], value)))
    
    def nnsrl_test(**kwargs):
        sha1sum = kwargs['sha']
        
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

    # create the scan parser
    get_parser = subparsers.add_parser('get',
                                       help='get the entry from database')
    get_parser.add_argument('-t',
                            '--type',
                            type=str,
                            choices=['file', 'os', 'manufacturer', 'product'],
                            help='type of the record')
    get_parser.add_argument('database',
                            type=str,
                            help='database to read NSRL records')
    get_parser.add_argument('key',
                            type=str,
                            help='key to retreive')
    get_parser.set_defaults(func=nsrl_get)


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