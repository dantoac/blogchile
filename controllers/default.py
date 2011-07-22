# -*- coding: utf-8 -*-
import locale
locale.setlocale(locale.LC_TIME, 'es_CL.UTF8')

response.title = 'Blogs Chilenos'

def index():
    response.meta.description = 'Blogs de noticias, tecnología, opinión, deporte, diseño, ocio, música, política, arte y más en la blogósfera chilena'
    return dict()

def votar():
    return locals()


#@auth.requires(request.cid)
def feed():
    #redirect(URL('index'))
    from gluon.tools import prettydate
    import locale
    locale.setlocale(locale.LC_ALL,locale='es_CL.UTF8')

    try:
        catslug = request.args(0) or db.categoria[1].slug
    except Exception,e:
        #redirect(URL(c='default',f='user'))
        response.flash = e
        catslug = ''
    response.title = "Blogs Chilenos. Blogósfera %s" % catslug.capitalize().replace('-',' ')
    response.meta.keywords = catslug.replace('-',' ')
    response.meta.description = "Los mejores blogs de %s en la blogósfera chilena; últimos artículos" % catslug.capitalize().replace('-',' ')
    """
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = 'max-age=60'
    """
    # obteniendo el id, nombre y slug de las categorías registradas


    # obteniendo la petición de categoría desde la url, sino setea por defecto la primera conocida en db

    feed_ids = entradas = []
    box = DIV(_class = 'box')

    #entradas = DIV()
    rss = {}
    lista_fidx = []
    # obteniendo los feeds categorizados bajo el slug solicitado desde la url

    #### 1 categoría por feed
    for feedincat in db((db.categoria.slug == catslug) & (db.feed.categoria == db.categoria.id)
                #& (db.feed_categoria.feed == db.feed.id)
                #& (db.feed_categoria.is_active == True)
                & (db.feed.is_active == True)
                & (db.categoria.is_active == True)
                ).select(db.feed.ALL):

        #lista_fidx.append(feedincat.id) <- desde aquí podŕia también actualizar u2d_cat()
        feedbox = DIV(DIV(A(feedincat.title,_href=feedincat.source,_target='_blank'), _class = 'feed_titulo'), _class = 'feedbox feed_bloque  izq')

        for n in db(db.noticia.feed == feedincat.id).select(db.noticia.ALL, orderby =~ db.noticia.id, limitby=(0,3)):

            if n.updated != None:
                actualizado = n.updated
            else:
                actualizado = n.created_on

            # armando la url que va en el rss
            localurl = 'http://' + request.env.http_host + URL(c = 'default', f = 'go.html', args = [n.slug,n.id], extension='html')

            # armando el bloque para la visa en html
            feedbox.append(DIV(DIV(A(n.title.lower()+'...', _name = n.slug, _href = URL(r = request, f = 'go.html', args = [n.slug,n.id]), _class = 'noticia_link', _target='_blank', extension='html'), _class = 'noticia_contenido'), DIV(prettydate(actualizado, T), _class = 'noticia_meta'), _class = 'noticia'))

            entradas.append(dict(title =unicode(n.title,'utf8'), link = localurl, description = unicode('%s (%s)' % (n.description, n.feed.title),'utf8'), created_on = request.now))


        box.append(feedbox)

    if request.extension == 'rss':
       rss = dict(title = request.application.upper(),
                  link = 'http://' + request.env.http_host + request.url,
                  description = unicode(response.meta.description, 'utf8'),
                  created_on = request.now,
                  entries = entradas
                  )
       contenido = rss
    else:

       contenido = dict(box = box)

    return response.render(contenido)


def elimina_tildes(s):
    """
    Esta función sirve para eliminar las tildes del string que
    se le pase como parámetro.
    """
    import unicodedata
    normalizado = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    return str(normalizado)


def go():
    if request.extension!='html':
        request.extension = 'html'

    response.files.append(URL('static','css/go.css'))

    slugnoticia = request.args(0) #para mostrar la noticia en la url; SEO
    nid = request.args(1)

    #titulo = db.noticia[nid].title
    titulo = slugnoticia.capitalize().replace('-',' ')

    categoria = db.noticia[nid].feed.categoria.title

    response.title='%s: %s' % (categoria.capitalize(),titulo.capitalize())
    response.meta.description = '%s %s' % (response.title,db.noticia[nid].feed.title)

    shorturl = db.noticia[nid].shorturl
    #titulo = db.noticia[nid].title

    if 'http://lmddgtfy' in shorturl:
        response.flash = 'El enlace se ha perdido por algún motivo. Te dirigiremos a una búsqueda privada al respecto.'

    if request.env.http_referer!=None:
        goback = A(SPAN(_class = 'icon leftarrow'), 'Volver', _class = 'button', _style = 'margin-bottom:1em;float:left;',
                   _href = request.env.http_referer)
    else:
        goback = A(SPAN(_class = 'icon home'), 'Blogosfera.cl', _class = 'positive primary button', _style = 'margin-bottom:1em;float:left;',
                   _href = 'http://blogosfera.cl')

    #cerrarmarco = A(SPAN(_class = 'icon cross'), 'Ir a la Fuente', _class = 'negative button', _style = 'margin-bottom:1em;float:right;', _href = shorturl)

    referer = DIV(goback)
    go = DIV(IFRAME(_src = shorturl, _style = 'height:inherit;width:inherit;border:0;'), _id = 'godiv', _style = 'display:block;height:100%;width:100%;')

    return dict(go=go,shorturl=shorturl,referer=referer)


@auth.requires(request.cid)
def misfeeds():
    fdata = db(db.feed.created_by == auth.user_id).select(db.feed.id,db.feed.title,db.feed.categoria,db.feed.is_active)
    ftable = TABLE(THEAD(TR(TH('Título'),TH('Categoría'),TH('Activado'))))
    for f in fdata:
        ftable.append(TR(TD(f.title),TD(f.categoria.title),TD(f.is_active),TH(A(SPAN(_class='icon pen'),'Editar',_href=URL(c='default',f='editarFeed.load',args=[f.id]),_class='negative button',cid='editmyfeed'))))

    return dict(ftable=ftable)

@auth.requires(request.cid)
def editarFeed():
    db.feed.is_active.readable=True
    db.feed.is_active.writable=True
    form = ''
    if request.args(0):
        if db.feed[int(request.args(0))].created_by == auth.user_id:
            form = SQLFORM(db.feed,request.args(0),deletable=True)
            if form.accepts(request.vars,session):
                response.flash = 'El Feed ha sido editado exitosamente'

        else:
            response.flash = 'El feed que referencias no es válido'
    return dict(form=form)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form = auth())

def sitemap():
    if request.extension == 'xml':
        sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]
        prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host
        for cat in db((db.categoria.id>0) & (db.categoria.is_active == True)).select(db.categoria.id,db.categoria.title,db.categoria.slug):
            sm.append(str(TAG.url(
                TAG.loc(prefix,URL(r=request,c='default',f='respira.',args=[cat.slug])),
                TAG.changefreq('always')
                )))
            sm.append(str(TAG.url(
                TAG.loc(prefix,URL(r=request,c='default',f='feed.rss',args=[cat.slug])),
                TAG.changefreq('always')
                )))
        sm.append('</urlset>')
        return sm
    elif request.extension == 'html':
        #response.view = 'plantilla.html'
        sm = DIV(_id='sitemap')

        for cat in db((db.categoria.id>0) & (db.categoria.is_active==True)).select(db.categoria.id,db.categoria.title,db.categoria.slug):

            categorias = DIV(H2(A(cat.title.capitalize(),_href=URL(r=request,c='default',f='respira.',args=[cat.slug]))))
            noticias = UL()

            data = db((db.feed.categoria == cat.id)& (db.noticia.feed == db.feed.id)).select(db.noticia.id, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(0,3))
            for noti in data:
                noticias.append(LI(A(noti.title, _href=URL(c='default',f='go',args=[noti.slug,noti.id]))))
            categorias.append(noticias)
            sm.append(categorias)
        return dict(sm=sm)

def sitemapindex():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]

    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host

    for i in xrange(1,5):
        sm.append(str(TAG.sitemap(
            TAG.loc(prefix,URL(c='default',f='sitemap%s.xml' % i))
            )))

    sm.append('</sitemapindex>')
    return sm


def sitemap1():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]

    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host

    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(0,10000))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='go',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))

    sm.append('</urlset>')
    return sm

def sitemap2():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]

    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host

    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(10000,20000))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='go',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))

    sm.append('</urlset>')
    return sm

def sitemap3():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]

    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host

    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(20000,30000))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='go',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))

    sm.append('</urlset>')
    return sm

def sitemap4():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]

    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host

    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(30000,40000))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='go',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))

    sm.append('</urlset>')
    return sm



# URLs ANTIGUAS. Las funciones a continuación están sólo para compatibilidad retroactiva

def respira():
    return redirect(URL(c='default',f='index',args=request.args))


def buscar():
    if request.args or request.vars:
        return redirect(URL(c='buscar',f='index',vars={'q':request.args}))
    else:
        return redirect(URL(c='buscar',f='index'))
