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

import os
os.environ['TZ']='America/Santiago'
from random import choice
#session.forget()

xurl_service = ['http://go.gnu.cl/api.php?url',
            #'http://xurl.cl/api.php?url',
            #'http://to.ly/api.php?longurl',
            'http://tinyurl.com/api-create.php?url',
            'http://is.gd/create.php?format=simple&url']


def _u2d(feedlink):
    import gluon.contrib.feedparser as feedparser
    import urllib2
    

    fidx = feedlink[0]
    flink = feedlink[1]

    
    feed = feedparser.parse(flink)

    maxfeeds = 4
    limite = 0

    #print('%s: %s' % (request.now.now(),db.feed[fidx].title)) ###################### !
    for e in feed.entries:
        # revisando si el artículo obtenido ya estaba en la db
        #edata = db((db.noticia.feed == fidx) & (db.noticia.title == XML(e.title))).select(db.noticia.id)

        if limite == maxfeeds:
            break

        try:
            xurl_api = choice(xurl_service)
            xurl = urllib2.urlopen("%(api)s=%(longurl)s" % dict(api=xurl_api,longurl=e.link)).read()
        except Exception,e:
            print('No se pudo acortar la url: %s' % e)
            continue

        
        #last8news = db(db.noticia).count() - 8
        no_existe = db((db.noticia.title.contains(XML(e.title)))).isempty()
        #si no encuentra nada, inserta en la db, sino no hace nada
        if no_existe:
            
            print('\t%s' % xurl)

            try:
                actualizado=e.updated
            except:
                actualizado=request.now.now()

            try:
                DESCRIPTION = e.description
            except:
                DESCRIPTION = e.link

            try:
                db.noticia.insert(title = XML(e.title), link = e.link, description = XML(DESCRIPTION),
                                  updated = actualizado, created_on=request.now.now(), feed = fidx, shorturl=xurl)
                db.commit()
            except Exception,e:
                print('Error registrando noticia: %s' % e)
            limite += 1
        else:
            print('Ya existe entre las últimas 8 noticias')
            continue
        

'''
feed_data = db((db.feed.id>0) & 
           (db.feed.is_active==True) &
           (db.feed.categoria < 3)
           ).select(db.feed.id)
'''
links = [(f.id,f.link) for f in db((db.feed.id>0) & 
                                   (db.feed.is_active==True)).select()]

#try:
for feedlink in links:
    
    _u2d(feedlink)    
        #except Exception,e:
        #    print "Excepción: %s" % e
