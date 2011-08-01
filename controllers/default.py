# -*- coding: utf-8 -*-
import locale
locale.setlocale(locale.LC_TIME, 'es_CL.UTF8')
#response.title = 'Blog Chile'

def index():
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = 'max-age=600'
    response.files.append(URL('static','js/jquery.cycle.all.min.js'))

    if request.args(0):
        catslug = request.args(0)
        response.title = "Blog Chile: %s" % catslug.capitalize().replace('-',' ')
        response.meta.keywords = catslug.replace('-',' ')
        response.meta.description = "Blog de %s en Chile, Blogósfera Chilena, Blogs Chilenos," % catslug.capitalize().replace('-',' ')
    else:
        response.meta.description = 'Blogs de Chile, noticias, tecnología, opinión, deporte, diseño, ocio, música, política, arte y más en la blogósfera chilena'
        response.meta.keywords = 'blogs chile, turismo chile, blogs chilenos'

    if request.extension == 'rss':
        return redirect('http://feeds.feedburner.com/blogosfera/dDKt')

    # muestra un response.flash con la descripción de cada categoría, si es que la hay (en db.feed)
    if request.args:
        descrip = db(db.categoria.slug == request.args(0)).select(db.categoria.description)[0].description
        if descrip != None:
            response.flash = descrip

    # aviso temporal de WIP. chk según sessión de conexión en el sitio
    if session.avisado == False:
        response.flash = XML('El Sitio está temporalmente bajo algunos ajustes extraordinarios; disculpa si te ocasionan alguna molestia: %s ' % session.avisado)        
        session.avisado = True

    return dict()

def votar():
    return locals()

@auth.requires(request.cid)
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
    
    # obteniendo el id, nombre y slug de las categorías registradas


    # obteniendo la petición de categoría desde la url, sino setea por defecto la primera conocida en db

    feed_ids = entradas = []
    blogs = DIV()

    #entradas = DIV()
    rss = {}
    lista_fidx = []
    # obteniendo los feeds categorizados bajo el slug solicitado desde la url

    Google_ad = DIV(XML('''<script type="text/javascript"><!--
google_ad_client = "ca-pub-9647318851151478";
/* bloque-txt-120x240 */
google_ad_slot = "0858517491";
google_ad_width = 120;
google_ad_height = 240;
//-->
</script>
<script type="text/javascript"
src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>'''), _class='feed_bloque izq')


    #### 1 categoría por feed
    for feedincat in db((db.categoria.slug == catslug) & (db.feed.categoria == db.categoria.id)
                #& (db.feed_categoria.feed == db.feed.id)
                #& (db.feed_categoria.is_active == True)
                & (db.feed.is_active == True)
                & (db.categoria.is_active == True)
                ).select(db.feed.ALL):

        #lista_fidx.append(feedincat.id) <- desde aquí podŕia también actualizar u2d_cat()

        # armando feed_bloque y la noticia de cada feed
        feedbox = DIV(DIV(A(feedincat.title,_href=feedincat.source,_target='_blank'), _class = 'feed_titulo'), _class = 'feedbox feed_bloque  izq')

        for n in db(db.noticia.feed == feedincat.id).select(db.noticia.ALL, orderby =~ db.noticia.id, limitby=(0,4)):

            if n.updated != None:
                actualizado = n.updated
            else:
                actualizado = n.created_on

            # armando la url que va en el rss
            localurl = 'http://' + request.env.http_host + URL(c = 'default', f = 'go.html', args = [n.slug,n.id], extension='html')

            # armando el título y enlace a la publicación; armando los bloques de publicación
            feedbox.append(DIV(DIV(A(n.title.lower()+'...', _name = n.slug, _href = URL(r = request, f = 'go.html', args = [n.slug,n.id]), _class = 'noticia_link', _target='_blank', extension='html'),DIV(prettydate(actualizado, T), _class = 'noticia_meta'), _class = 'noticia_contenido'), _class = 'noticia'))

            
            entradas.append(dict(title =unicode(n.title,'utf8'), link = localurl, description = unicode('%s (%s)' % (n.description, n.feed.title),'utf8'), created_on = request.now))
        
        blogs.append(feedbox)
        #box.append(google_ad)
    #'''
    if request.extension == 'rss':

        feedburner = {'portada':'http://feeds.feedburner.com/blogosfera/dDKt'}



        rss = dict(title = request.application.upper(),
                   link = 'http://' + request.env.http_host + request.url,
                   #description = unicode(response.meta.description, 'utf8'),
                   description = '',
                   created_on = request.now,
                   entries = entradas
                   )
        contenido = rss
    else:
        response.view = 'default/feed.load'
        contenido = dict(blogs = blogs)
      
    return response.render(contenido)
    #'''
    #return dict(blogs=blogs)

def elimina_tildes(s):
    """
    Esta función sirve para eliminar las tildes del string que
    se le pase como parámetro.
    """
    import unicodedata
    normalizado = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    return str(normalizado)

def blog():
    if request.extension!='html':
        request.extension = 'html'

    response.files.append(URL('static','css/blog.css'))
    #response.files.append(URL('static','js/jquery.iframe.js'))

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
        goback = A(SPAN(_class = 'icon leftarrow'), 'Regresar', _title='Volver a la página anterior', _class = 'button izq',
                   _href = request.env.http_referer)
    else:
        goback = A(SPAN(_class = 'icon home'), 'Blogosfera.cl', _class = 'positive primary button izq',
                   _href = 'http://blogosfera.cl/')

    cerrarmarco = A(SPAN(_class = 'icon cross'), 'Ir al Blog', _class = 'negative button der', _href = shorturl, _title='Cerrar este marco y visitar el artículo en el blog de su fuente original')

    referer = goback
    #referer = DIV(goback, class='izq')
    
    go = DIV(IFRAME(_src = shorturl, _style = 'height:90%;width:inherit;border:0;'), _id = 'godiv', _style = 'display:block;height:100%;width:100%;')
    """
    go = DIV(SCRIPT('$("<iframe/>").src("%s").appendTo("body");' % shorturl),SCRIPT('''$("iframe").src("%s", function(iframe, 10000) {
alert("That took " + duration + " ms.");
}, {
  timeout: function() { alert("oops! timed out."); },
  timeoutDuration: 10000
});''' % shorturl))
    """

    #go = DIV(jqiframe, _id = 'godiv')

    #response.flash = shorturl

    return dict(go=go,shorturl=shorturl,referer=referer,cerrarmarco=cerrarmarco)


@auth.requires(request.cid)
def misfeeds():
    fdata = db(db.feed.created_by == auth.user_id).select(db.feed.id,db.feed.title,db.feed.categoria,db.feed.is_active,orderby=db.feed.id)
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

            data = db((db.feed.categoria == cat.id)& (db.noticia.feed == db.feed.id)).select(db.noticia.id, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(0,4))
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


def sitemap5():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]
    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host
    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(40000,50000))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='go',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))
    sm.append('</urlset>')
    return sm

def smpaginas():
    
    return sm


# URLs ANTIGUAS. Las funciones a continuación están sólo para compatibilidad retroactiva

def respira():
    if request.extension == 'rss':
        return redirect(URL(c='default',f='feed.rss', args=request.args))
    else:
        return redirect(URL(c='default',f='index',args=request.args))


def buscar():
    if request.env.http_referer == request.url:
        response.flash = 'Puedes buscar directamente usando: buscar?q=termino+de+busqueda'
        if request.args:        
            return redirect(URL(c='default',f='buscar',vars={'q':request.args}))
    else:                    
        form = FORM(INPUT(_name='q'),INPUT(_type='submit', _value='Buscar'))
        if form.accepts(request.vars,session):
            redirect(URL(c='default',f='buscar',vars={'q':request.post_vars.q}))    
        return dict(form=form)

def go():
    return redirect(URL(r=request,c='default',f='blog',args=request.args))
