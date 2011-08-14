# -*- coding: utf-8 -*-
'''
Este script permite la actualización de los feeds evitando que 2 procesos
se superpongan como podría pasar al usar cron para estos efectos.

USO:
python2 web2py/web2py.py -S vortex -M -N -R ~/web2py/applications/vortex/private/actualiza_feeds.py

NECESITA LA LIBERARÍA dateutil <http://niemeyer.net/python-dateutil>

daniel@varpub.org
'''
import time
#from subprocess import Popen

#session.forget()

xurl_service = ['http://go.gnu.cl/api.php?url',
            #'http://xurl.cl/api.php?url',
            #'http://to.ly/api.php?longurl',
            'http://tinyurl.com/api-create.php?url']


def _u2d(fidx):
    import gluon.contrib.feedparser as feedparser
    import urllib2
    from random import choice
    feed = feedparser.parse(db.feed[fidx].link)
    maxfeeds = 3
    limite = 0

    print('%s: %s' % (request.now,db.feed[fidx].title))
    for e in feed.entries:
        # revisando si el artículo obtenido ya estaba en la db
        edata = db((db.noticia.feed == fidx) & (db.noticia.title == XML(e.title))).select(db.noticia.id)

        if limite == maxfeeds:
            break
        
        #si no encuentra nada, inserta en la db, sino no hace nada
        if len(edata) == 0:
            xurl_api = choice(xurl_service)
           
            try:
                xurl = urllib2.urlopen("%(api)s=%(longurl)s" % dict(api=xurl_api,longurl=e.link)).read()
            except:
                xurl = urllib2.urlopen("%(api)s=%(longurl)s" % dict(api=xurl_api,longurl=e.link)).read()

            print('\t%s' % xurl)

            try:
                actualizado=e.updated
            except:
                actualizado=request.now

            #ddg="http://lmddgtfy.com/?q=%(term)s+%(sitio)s" % dict(term=XML(e.title),sitio=XML(db.feed[fidx].title))
            #ddg = "http://lmddgtfy.com/?q=%(term)s+%(sitio)s" % dict(term=e.slug.replace('-',' '),sitio=XML(e.feed.title))
            try:
                DESCRIPTION = e.description
            except:
                DESCRIPTION = e.link
        
            db.noticia.insert(title = XML(e.title), link = e.link, description = XML(DESCRIPTION),
                              updated = actualizado, created_on=request.now, feed = fidx, shorturl=xurl)#, slug = slug)
            db.commit()

        limite += 1
        


#while True:
    ### para varias categorías por feed
    #~ feed_data = db((db.feed_categoria.categoria == db.categoria.id)# & (db.categoria.slug == catslug)
                   #~ & (db.feed_categoria.feed == db.feed.id)
                   #~ & (db.feed_categoria.is_active == True)
                   #~ & (db.feed.is_active == True)
                   #~ & (db.categoria.is_active == True)
                   #~ ).select()

    # para 1 categoría por feed
feed_data = db((db.feed.categoria == db.categoria.id)
            #& (db.feed_categoria.feed == db.feed.id)
            #& (db.feed_categoria.is_active == True)
            & (db.feed.is_active == True)
            & (db.categoria.is_active == True)
            ).select(db.feed.id)
#try:
for feed in feed_data:
    fidx = feed.id
    _u2d(fidx)
        #time.sleep(3) #en segundos
#except Exception,e:
#    print "excepcion: %s" % e
