# -*- coding: utf-8 -*-
import locale
locale.setlocale(locale.LC_ALL, 'es_CL.UTF8')

#@cache(request.env.path_info, time_expire=150, cache_model=cache.ram)
def index():
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = 'max-age=300'
    

    # redirecciona a feedburner (los rss se generan en c=feed)
    if request.extension == 'rss':
        if request.args(0) == None:
            cat = ''
        else:
            cat = request.args(0)
        return redirect('http://feeds.feedburner.com/blogchile%s' % cat)

    # verificamos si pasó por c=default f=mobile y activó el bit de sesión
    if session.mobile:
        response.view = 'default/index.mobi'
        response.files.append(URL('static','css/blogchilemobile.css'))
    else:

        ''' si no hay bit de sesión mobile, establece el caché del browserl
        esto es por que sino el caché impediría cambiar al modo mobile (bug de flojo)'''

        response.files.append(URL('static','js/jquery.cycle.all.min.js'))

    if request.args(0):
        catslug = request.args(0)
        response.title = 'Blog Chile: %s' % catslug.capitalize().replace('-',' ')
        response.meta.keywords = catslug.replace('-',' ')
        response.meta.description = "Blog de %s en Chile, Blogósfera Chilena, Blogs Chilenos," % catslug.capitalize().replace('-',' ')
        if catslug in ['medio-ambiente','animales']:
            return redirect(URL(r=request,f='index',args='naturaleza'),301)
    else:
        response.title = 'Blog Chile: Portada'
        response.meta.description = 'Blogs de Chile: Últimas publicaciones de noticias, tecnología, opinión, deporte, diseño, ocio, música, política, arte y más en la blogósfera chilena'
        response.meta.keywords = 'blogs chile, turismo chile, blogs chilenos'

    #if request.extension == 'rss':
    #    return redirect('http://feeds.feedburner.com/blogosfera/dDKt')

    try:
        # muestra un response.flash con la descripción de cada categoría, si es que la hay (en db.feed)
        if request.args:
            descrip = db(db.categoria.slug == request.args(0)).select(db.categoria.description)[0].description
            if descrip != None:
                response.flash = descrip
    except:
        pass
    # aviso temporal de WIP. chk según sessión de conexión en el sitio
    """
    if session.avisado == False:
        response.flash = XML('El Sitio está temporalmente bajo algunos ajustes extraordinarios; disculpa si te ocasionan alguna molestia: %s ' % session.avisado)        
        session.avisado = True
    """

    publicaciones = LOAD(r=request,c='default',f='publicaciones.load',args=request.args,ajax=True,content='Cargando bloques...')
    
    return dict(publicaciones=publicaciones)
    #return dict()

#@cache(request.env.path_info, time_expire=150, cache_model=cache.disk)
def publicaciones():
    if not request.ajax: return ''
    from gluon.tools import prettydate
    from datetime import datetime

    if request.args:
            catslug_data = db(db.categoria.slug == request.args(0)).select(db.categoria.slug)
            for cat in catslug_data:
                    catslug = cat.slug
    else:
            catslug = 'noticias'


    publicaciones = DIV()

    # obteniendo los feeds categorizados bajo el slug solicitado desde la url

    ### 1 categoría por feed
    """
    for feedincat in db((db.categoria.slug == catslug) & (db.feed.categoria == db.categoria.id)
                            #& (db.feed_categoria.feed == db.feed.id)
                            #& (db.feed_categoria.is_active == True)
                            & (db.feed.is_active == True)
                            & (db.categoria.is_active == True)
                            ).select(db.feed.ALL):
    """

    feedincat_data = db((db.categoria.slug == catslug)
                                            & (db.feed.categoria == db.categoria.id)
                                            & (db.feed.is_active == True)
                                            & (db.categoria.is_active == True)
                                            ).select(db.feed.id,db.feed.title,db.feed.source)


    for feedincat in feedincat_data:

            # armando feed_bloque y la noticia de cada feed
            feedbox = DIV(DIV(A(feedincat.title,_href=feedincat.source,_target='_blank',_class='ui-widget-header-a'), _class = 'feed_titulo ui-widget-header ui-corner-all'), _class = 'feedbox feed_bloque  izq ui-widget ui-corner-all')

            for n in db(db.noticia.feed == feedincat.id).select(db.noticia.ALL, orderby =~ db.noticia.id, limitby=(0,4)):


                    try:
                        actualizado = datetime.strptime(str(n.updated),'%Y-%m-%d %H:%M:%S')
                    except:
                        actualizado = n.created_on

                    # armando la url que va en el rss
                    #localurl = 'http://' + request.env.http_host + URL(c = 'default', f = 'blog.html', args = [n.slug,n.id], extension='html')

                    # armando el título y enlace a la publicación; armando los bloques de publicación
                    feedbox.append(DIV(DIV(A(n.title.lower()+'...', _name = n.slug, 
                                             _href = URL(r = request, f = 'blog', args = [catslug,n.slug,n.id], extension=False), 
                                             _class = 'noticia_link ui-widget-content-a', _target='_blank',extension='html'),
                                             DIV(prettydate(actualizado,T),
                                                 _class='noticia_meta'),
                                                 _class = 'noticia_contenido ui-widget-content ui-corner-all'),
                                                 _class = 'noticia ui-widget ui-corner-all')
                        )


                    #entradas.append(dict(title =unicode(n.title,'utf8'), link = localurl, description = unicode('%s (%s)' % (n.description, n.feed.title),'utf8'), created_on = request.now))


            publicaciones.append(feedbox)

    response.js = XML('''function filtro(){
jQuery("#filtrando").keyup(function () {
    var filter = jQuery(this).val(), count = 0;

    jQuery(".feedbox .noticia, .feed_titulo").each(function () {
            if (jQuery(this).text().search(new RegExp(filter, "i")) < 0) {
                    jQuery(this).addClass("hidden");
            } else {
                    jQuery(this).removeClass("hidden");
                    count++;
            }
    });
    jQuery("#filtrado").text(count);
});
}

jQuery(document).ready(filtro);
''')

    d = dict(publicaciones=publicaciones)
    return response.render(d)
    #return dict(publicaciones=publicaciones)

    
def elimina_tildes(s):
    """
    Esta función sirve para eliminar las tildes del string que
    se le pase como parámetro.
    """
    import unicodedata
    normalizado = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    return str(normalizado)

#@cache(request.env.path_info, time_expire=1200, cache_model=cache.disk)
def blog():
    if request.extension!='html':
        request.extension = 'html'

    response.files.append(URL('static','css/blog.css'))
    #response.files.append(URL('static','js/jquery.iframe.js'))

    catslug = request.args(0)
    slugnoticia = request.args(1) #para mostrar la noticia en la url; SEO
    nid = request.args(2)
    #nid = int(request.args[len(request.args)-1])


    #titulo = db.noticia[nid].title
    #print(type(nid))
    
    titulo = slugnoticia.replace('-',' ')

    categoria = catslug

    response.title='%s: %s' % (categoria.capitalize(),titulo.capitalize())
    #response.meta.description = '%s %s' % (response.title,db.noticia[nid].feed.title)

    if db.noticia(nid):
        shorturl = db.noticia(nid).shorturl
    else:
        shorturl = 'http://lmddgtfy.net/?q=%s, %s' % (request.args(0).title(),request.args(1).title().replace('-',' '))


    if 'http://lmddgtfy' in shorturl:
        response.flash = 'El enlace se ha perdido. Te dirigiré a una búsqueda privada usando DuckDuckGo.com. Disculpa las molestias.'
        
    if request.env.http_referer!=None:
        goback = A(SPAN(_class = 'icon leftarrow'), 'Regresar', _title='Volver a la página anterior', _class = 'pill button izq',
                   _href = request.env.http_referer)
    else:
        goback = A(SPAN(_class = 'icon home'), 'Blogchile.cl', _class = 'positive primary button izq',
                   _href = 'http://blogchile.cl/')

    cerrarmarco = A(SPAN(_class = 'icon rightarrow'), 'Ir al Blog', _class = 'pill negative button der', _href = shorturl, _title='Cerrar este marco y visitar el artículo en el blog de su fuente original')

    referer = goback
    #referer = DIV(goback, class='izq')
    
    #go = DIV(IFRAME(_src = shorturl, _style = 'height:90%;width:inherit;border:0;'), _id = 'godiv', _style = 'display:block;height:100%;width:100%;')
    blog = IFRAME(_src = shorturl, _id='blogiframe', _style='width:inherit;border:0;')
    
    d = dict(blog=blog,shorturl=shorturl,referer=referer,cerrarmarco=cerrarmarco)
    return response.render(d)






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
    del response.headers['Cache-Control']
    del response.headers['Pragma']
    del response.headers['Expires']
    response.headers['Cache-Control'] = 'max-age=300'
    
    if request.extension == 'xml':
        sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]
        prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host
        for cat in db((db.categoria.id>0) & (db.categoria.is_active == True)).select(db.categoria.id,db.categoria.title,db.categoria.slug):
            sm.append(str(TAG.url(
                TAG.loc(prefix,URL(r=request,c='default',f='index.html',args=[cat.slug])),
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

            categorias = DIV(H2(A(cat.title.capitalize(),_href=URL(r=request,c='default',f='index.html',args=[cat.slug]))))
            noticias = UL()

            data = db((db.feed.categoria == cat.id)& (db.noticia.feed == db.feed.id)).select(db.noticia.id, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(0,4))
            for noti in data:
                noticias.append(LI(A(noti.title, _href=URL(c='default',f='blog',args=[noti.slug,noti.id]))))
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

    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, orderby=~db.noticia.id, limitby=(0,200))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='blog',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))

    sm.append('</urlset>')
    return sm

def sitemap2():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]

    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host

    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(200,400))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='blog',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))

    sm.append('</urlset>')
    return sm

def sitemap3():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]

    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host

    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(400,600))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='blog',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))

    sm.append('</urlset>')
    return sm

def sitemap4():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]
    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host
    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(600,800))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='blog',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))
    sm.append('</urlset>')
    return sm


def sitemap5():
    sm = [str('<?xml version="1.0" encoding="UTF-8" ?> <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')]
    prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host
    data = db(db.noticia.id>0).select(db.noticia.id, db.noticia.created_on, db.noticia.title, db.noticia.slug, distinct=True, orderby=~db.noticia.id, limitby=(800,1000))
    for noti in data:
        sm.append(str(TAG.url(
            TAG.loc(prefix,URL(c='default',f='blog',args=[noti.slug,noti.id],extension='')),
            TAG.lastmod(noti.created_on.date()),
            TAG.changefreq('always')
            )))
    sm.append('</urlset>')
    return sm


####################################################################################
# URLs ANTIGUAS. Las funciones a continuación están sólo para compatibilidad retroactiva
####################################################################################
def respira():
    if request.extension == 'rss':
        return redirect(URL(c='default',f='feed.rss', args=request.args),301)
    else:
        return redirect(URL(c='default',f='index',args=request.args),301)


def buscar():
    if request.env.http_referer == request.url:
        response.flash = 'Puedes buscar directamente usando: buscar?q=termino+de+busqueda'
        if request.args:        
            return redirect(URL(c='default',f='buscar',vars={'q':request.args}),301)
    else:                    
        form = FORM(INPUT(_name='q'),INPUT(_type='submit', _value='Buscar'))
        if form.accepts(request.vars,session):
            redirect(URL(c='default',f='buscar',vars={'q':request.post_vars.q}),301)    
        return dict(form=form)

def go():
    return redirect(URL(r=request,c='default',f='blog',args=request.args),301)

def feed():
    if request.extension == 'rss':
        return redirect(URL(r=request,c='default',f='index.rss',args=request.args(0)),301)
    else:
        return redirect(URL(r=request,c='default',f='index',args=request.args(0)),301)
