
from applications.shared.modules.stickon.tools import ModelDb

model_db = ModelDb(globals())
db = model_db.db
auth = model_db.auth
crud = model_db.crud
service = model_db.service
mail = model_db.mail
local_settings = model_db.local_settings

#########################################################################
## Define your tables below, for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

"""
account     # Copied from accounting. Used by test_database.py

company_id          integer     Reference to accounting.company.id
number              integer     A unique number accounting account number.
name                text        Name of the account.
account_type_id     integer     Reference to accounting.account_type.id.
parent_account_id   integer     Account this account is a subgroup of. Reference to accounting.account.id.
posting             boolean     0=non-posting, 1=posting
zero_balance        boolean     0=no, 1=yes. Account regularly balances to zero. Eg credit card, ledger transfer, HST payable.
status              text        Status of this status. 'a' = active, 'd'=deactive.
creation_date:      datetime    Record creation timestamp.
modified_date:      datetime    Record last modified timestamp.
"""
db.define_table('account',
    Field('company_id', 'integer'),
    Field('number', 'integer',
        requires=IS_INT_IN_RANGE(1000,10000)),
    Field('name'),
    Field('account_type_id', 'integer'),
    Field('parent_account_id', 'integer'),
    Field('posting', 'integer',
        requires=IS_INT_IN_RANGE(0,2)
        ),
    Field('zero_balance', 'integer',
        requires=IS_INT_IN_RANGE(0,2)
        ),
    Field('status',
        default='a',
        requires=IS_IN_SET(['a', 'd'])
        ),
    Field('creation_date', 'datetime',
        requires=IS_NULL_OR(IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'))),
        ),
    Field('modified_date', 'datetime',
        requires=IS_NULL_OR(IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'))),
        ),
    )

"""
company     # Copied from accounting. Used by test_database.py

name                    text        The name of the company.
bank_account_id         integer     Default account id if no others are found.  References to accounting.account.id.
hst_account_id          integer     HST account id.  References to accounting.account.id.
pst_account_id          integer     PST account id.  References to accounting.account.id.
transfer_account_id     integer     Ledger transfer account id.  References to accounting.accout.id.
unsorted_account_id     integer     Account id for unsorted entries.  References to accounting.account.id.
earnings_account_id     integer     Retained earnings account id. References to accounting.account.id.
opening_account_id      integer     Opening balance account id.  Reference to accounting.account.id.
dfa_account_id          integer     Depreciable Fixed Assets account id.  Reference to accounting.account.id.
colour                  text        What colour to use to identify this company.
fiscal_month            integer     What month is the year end for this company.
freeze_date             date        Records before freeze_date are read only.
creation_date:          datetime    Record creation timestamp.
modified_date:          datetime    Record last modified timestamp.
        requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d')))
"""
db.define_table('company',
    Field('name'),
    Field('bank_account_id', 'integer',
        requires=IS_NULL_OR(IS_IN_DB(db, db.account.id,'%(name)s'))),
    Field('hst_account_id', 'integer',
        requires=IS_NULL_OR(IS_IN_DB(db, db.account.id,'%(name)s'))),
    Field('pst_account_id', 'integer',
        requires=IS_NULL_OR(IS_IN_DB(db, db.account.id,'%(name)s'))),
    Field('transfer_account_id', 'integer',
        requires=IS_NULL_OR(IS_IN_DB(db, db.account.id,'%(name)s'))),
    Field('unsorted_account_id', 'integer',
        requires=IS_NULL_OR(IS_IN_DB(db, db.account.id,'%(name)s'))),
    Field('earnings_account_id', 'integer',
        requires=IS_NULL_OR(IS_IN_DB(db, db.account.id,'%(name)s'))),
    Field('opening_account_id', 'integer',
        requires=IS_NULL_OR(IS_IN_DB(db, db.account.id,'%(name)s'))),
    Field('dfa_account_id', 'integer',
        requires=IS_NULL_OR(IS_IN_DB(db, db.account.id,'%(name)s'))),
    Field('colour'),
    Field('fiscal_month', 'integer',
        requires=IS_INT_IN_RANGE(1,13)),
    Field('freeze_date', 'date',
        requires=IS_NULL_OR(IS_DATE())
        ),
    Field('creation_date', 'datetime',
        requires=IS_NULL_OR(IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'))),
        ),
    Field('modified_date', 'datetime',
        requires=IS_NULL_OR(IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S'))),
        ),
    )

"""
job         # Used by test_job_queue

start       datetime    # Start time. Job will not be run prior to this time.
priority    integer     # Priority of job, higher value = higher priority
command     varchar     # Command to execute.
status      char        # 'a' = active (queued),
                        # 'r' = running (in progress),
                        # 'd' = deactive (done)
created_on  datetime    # FIXME
updated_on  datetime    # FIXME
"""
db.define_table('job',
    Field('start',
        'datetime',
        requires=IS_DATETIME(),
        ),
    Field('priority',
        'integer',
        ),
    Field('command',
        'string',
        requires=IS_NOT_EMPTY(),
        ),
    Field('status',
        'string',
        requires=IS_IN_SET([('a', 'Enabled'), ('r', 'In Progress'),
            ('d', 'Disabled')], zero=None),
        ),
    Field('created_on',
        'datetime',
        writable=False,
        requires=IS_DATETIME(),
        ),
    Field('updated_on',
        'datetime',
        writable=False,
        requires=IS_DATETIME(),
        ),
    )

"""
setting                 # Used by test_setting

name         varchar     # FIXME
label        varchar     # FIXME
value        varchar     # FIXME
description  varchar     # FIXME
"""
db.define_table('setting',
    Field('name',
        'string',
        requires=IS_NOT_EMPTY(),
        ),
    Field('label',
        'string',
        requires=IS_NOT_EMPTY(),
        ),
    Field('value',
        'string',
        requires=IS_NOT_EMPTY(),
        ),
    Field('description',
        'string',
        requires=IS_NOT_EMPTY(),
        ),
    )

