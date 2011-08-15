# -*- coding: utf-8 -*-
import locale
locale.setlocale(locale.LC_TIME, 'es_CL.UTF8')

#url_prefix = request.env.wsgi_url_scheme+'://'+request.env.http_host
url_prefix = 'http://blogchile.cl'

response.generic_patterns = ['rss'] 

f = {'portada':'',
         'tecnología':'',
         'opinion':'',
         'mujer':'',
         'arte':'',
         'deporte':'',
         'eventos':'',
         'noticias':'',
         'ocio':'',
         'turismo':'',
         'videojuegos':'',
         'animales':'',
         'economía':'',
         }






def index():

    if request.args:
        catslug = request.args(0)
        
        data = db((db.noticia.feed == db.feed.id) & (db.feed.categoria == db.categoria.id) & (db.categoria.slug == catslug)).select(db.noticia.title,db.noticia.link,db.noticia.description,db.noticia.created_on,db.noticia.slug,db.noticia.id,db.noticia.updated,orderby=~db.noticia.id, limitby=(0,10))
        feed_title = unicode('BlogChile: %s' % catslug.capitalize(),'utf8')
        feed_url = unicode('http://blogchile.cl/index/%s' % catslug,'utf8')
        feed_description = unicode("Últimas publicaciones en blogs de %s" % catslug,"utf8")
    else:
        data = db(db.noticia.id>0).select(orderby=~db.noticia.id, limitby=(0,10))
        feed_title = unicode('BlogChile.cl: Todas las Categorías','utf8')
        feed_url = unicode('http://blogchile.cl/','utf8')
        #feed_description = unicode("Recopilación de las últimas publicaciones de entre todas las categorías","utf8"),
        feed_description=unicode('Recopilación de las últimas publicaciones de entre todas las categorías','utf8')

    entradas = {'title':'',
                'link':'',
                'description':'',
                'created_on':'',
                'pub_date':'',
                }

    e = []

    for pub in data:
        """
        entradas['title'] = XML(str(pub.title))
        entradas['link'] = URL(c='default',f='blog',args=[pub.slug,pub.id], extension=False)
        entradas['description'] = XML(str(pub.description))
        entradas['created_on'] = pub.created_on
        """
        entradas = dict(title=unicode(str(pub.title),'utf8'),
                        link = url_prefix+URL(c='default',f='blog',args=[pub.slug,pub.id], extension=False),
                        description = unicode(str(pub.description),'utf8'),
                        created_on = pub.updated,
                        pub_date = request.now
                        )

        e.append(entradas)

    feed = dict(title= feed_title,
                link = feed_url,
                description = feed_description,
                entries = e
                )

    return feed
    

