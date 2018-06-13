# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

import datetime

def get_user_email():
    return auth.user.email if auth.user is not None else None

#def get_current_time():

db.define_table('catInfor',
                Field('user_email', default = get_user_email()),
                Field('picture', 'upload', uploadfield='picture_file'),
                Field('picture_file', 'blob'),
                Field('cat_ID', 'integer',label="ID"),
                Field('catName',label="Name"),
                Field('catGender', label="Gender"),
                Field('catBreed', label="Breed"),
                Field('catAge', label="Age"),
                Field('catSize', label="Size"),
                Field('catColor', label="Color"),
                Field('catInfor','text', label="Information"),
                Field('is_available', 'boolean', default=True),
                Field('locationA'),
                Field('address'),
                Field('lat'),
                Field('lng'),
                Field('update_on','datetime', update=datetime.datetime.utcnow())
                )
db.catInfor.user_email.writable = False
db.catInfor.user_email.readable = False
db.catInfor.lat.readable = False
db.catInfor.lng.readable = False
db.catInfor.update_on.writable = db.catInfor.update_on.readable = False
db.catInfor.id.writable = db.catInfor.id.readable = False
db.catInfor.catGender.requires=IS_IN_SET(('Male', 'Female'))
db.catInfor.catSize.requires=IS_IN_SET(('Small', 'Median', 'Large'))

db.define_table('story',
                Field('user_email', default=get_user_email()),
                Field('title'),
                Field('author'),
                Field('datetime'),
                Field('story', 'text'),
                Field('update_on', 'datetime', update=datetime.datetime.utcnow()),
                Field('is_public', 'boolean', default=False),
                )

db.story.user_email.writable = False
db.story.user_email.readable = False
db.story.update_on.writable = db.story.update_on.readable = False
db.story.id.writable = db.story.id.readable = False

import datetime

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.define_table('user_images',
                Field('created_on', 'datetime', default=request.now),
                Field('created_by', 'reference auth_user', default=auth.user_id),
                Field('image_url'),
                Field('price', 'float')
                )


db.define_table('customer_order',
    Field('order_date', default=datetime.datetime.utcnow()),
    Field('customer_info', 'blob'),
    Field('transaction_token', 'blob'),
    Field('cart', 'blob'),
)

# Let's define a secret key for stripe transactions.
from gluon.utils import web2py_uuid
if session.hmac_key is None:
    session.hmac_key = web2py_uuid()

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)