# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
if 0:
    from gluon.sql import *
    from gluon.validators import *
#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
                                              # optional DAL('gae://namespace')
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL(['mysql://danto_bfra:040e10f4@localhost/danto_bfra'])       # if not, use SQLite or other DB
    '''
    acciones_readonly = ['feed']
    if request.controller != 'noticias':
        db = DAL(['sqlite://readonly.sqlite', 'postgres://danto:password@24d9a3a7/danto_planet'])
    else:
        db = DAL(['sqlite://storage2.sqlite'])
    '''
## if no need for session
#session.forget()

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(db) #Auth(globals(), db)                      # authentication/authorization
crud = Crud(globals(), db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'smtp.webfaction.com:25'  # your SMTP server
mail.settings.sender = 'robot@blogosfera.cl'         # your email
mail.settings.login = 'danto:d095af99'      # your credentials or None

auth.settings.hmac_key = 'sha512:73cad33d-37b6-46fa-8b25-f4e8d39b34c9'   # before define_tables()
auth.define_tables()                           # creates all needed tables

auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = False
auth.messages.verify_email = T('Te has registrado en http://blogosfera.cl. Haz clic en el siguiente enlace para verificar tu email: http://' + request.env.http_host + URL('default', 'user', args = ['verify_email']) + '/%(key)s')
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = T('En http://blogosfera.cl hemos recibido una solicitud de cambio de contraseña. Haz clic en el siguiente enlace para reiniciar tu constraseña: http://' + request.env.http_host + URL('default', 'user', args = ['reset_password']) + '/%(key)s')


auth.messages.label_first_name = 'Nombre'
auth.messages.label_last_name = 'Apellido'


## restricciones para auth
auth.settings.actions_disabled.append('register')

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled=['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None                      # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
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

tabla = db.define_table

tabla('categoria',
    Field('title', label = T('Nombre')),
    Field('slug', compute = lambda r:IS_SLUG.urlify(r['title'])),
    #Field('super', 'reference categoria', comment = 'SIN EFECTO todavía. Permitirá la jerarquización de categorías.'),
    #Field('freq', 'integer', requires = IS_INT_IN_RANGE(300, 604801, error_message = 'conozco desde 300 hasta 604800 '), label = T('Frecuencia de actualización'), comment = 'SIN USO AÚN'),
#    Field('actualizado', 'datetime', default = request.now, writable = False, readable = False),
    auth.signature,
    format = '%(title)s',
    )

### requerimientos tabla categoría
#db.categoria.super.requires = IS_EMPTY_OR(IS_IN_DB(db, 'categoria.id', '%(title)s', zero = T('[Seleccione sólo si corresponde]')))
db.categoria.title.requires = IS_NOT_IN_DB(db, 'categoria.title', error_message = 'ya hay una categoría con ese título')
db.categoria.is_active.writable = False
db.categoria.is_active.readable = False

tabla('feed',
    Field('categoria', 'reference categoria', comment = T('*requerido')),
    Field('title', label = T('Sitio'), comment = T('*requerido (sugerencia: "misitio.tld")')),
    #Field('description', 'text', label = T('Descripción'),comment=T('(opcional)')),
    Field('link', requires = IS_URL(), label = T('URL feed'), comment = T('*requerido')),
    auth.signature,
    format = '%(title)s',
    )

### requerimientos tabla feed
db.feed.is_active.writable = False;db.feed.is_active.readable = False
db.feed.link.requires = IS_NOT_IN_DB(db, 'feed.link', error_message = T('Esta URL ya está en los registros'))
db.feed.title.requires = IS_NOT_IN_DB(db, 'feed.title', error_message = T('Ya hay otro feed con este título'))
db.feed.categoria.requires = IS_IN_DB(db, 'categoria.id', '%(title)s', error_message = T('Debe caregorizar el feed para que pueda ser mostrado.'))


### SIN USAR, aún
tabla('feed_categoria',
    Field('feed', db.feed),
    Field('categoria', db.categoria, default = 1),
    auth.signature,
    )

### requerimientos tabla feed_caregoría
db.feed_categoria.is_active.writable = False
#****************** verificando que no se repita la relación feed_categoría
db.feed_categoria.feed.requires = IS_IN_DB(db, 'feed.id', '%(title)s', _and = IS_NOT_IN_DB(db(db.feed_categoria.categoria == request.vars.categoria), 'feed_categoria.feed', error_message = 'Este feed ya está asociado a esta categoría.'))


tabla('noticia',
      Field('title'),
      Field('slug', compute = lambda r:IS_SLUG.urlify(r['title'])),
      Field('link', requires = IS_URL()),
      Field('description', 'text'),
      Field('feed', db.feed),
      Field('updated', 'datetime', default=request.now),
      Field('shorturl',requires=IS_URL()),
      auth.signature,
      format = '%(slug)s',
      )

'''
tabla('votos_disponibles',
      Field('user','reference auth_user'),
      Field('feed_votados','list:reference feed'),
      Field('votos_disponibles','integer',default=3)
      )
'''
