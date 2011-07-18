# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('Respirando a Chile')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'webmaster@blogosfera.cl'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2011'


response.menubkn = DIV()

try:
        cats4menu = db((db.categoria.id > 0) & (db.categoria.is_active == True)).select(db.categoria.id, db.categoria.title, db.categoria.slug, orderby = db.categoria.slug)
        for cat in cats4menu:

            if cat.slug == request.args(0):

                if cat == cats4menu[len(cats4menu) - 1]:
                    response.menubkn.append(A(cat.title.capitalize()+' ', _href = URL(r = request, f = 'index', args = cat.slug), _class = 'primary pill button right boton_categoria_activa'))
                elif cat == cats4menu[0]:
                    response.menubkn.append(A(cat.title.capitalize()+' ', _href = URL(r = request, f = 'index', args = cat.slug), _class = 'primary pill button left boton_categoria_activa'))
                else:
                    response.menubkn.append(A(cat.title.capitalize()+' ', _href = URL(r = request, f = 'index', args = cat.slug), _class = 'primary pill button middle boton_categoria_activa'))
            else:
                if cat == cats4menu[len(cats4menu) - 1]:
                    response.menubkn.append(A(cat.title.capitalize()+' ', _href = URL(r = request, f = 'index', args = cat.slug), _class = 'pill button right'))
                elif cat == cats4menu[0]:
                    response.menubkn.append(A(cat.title.capitalize()+' ', _href = URL(r = request, f = 'index', args = cat.slug), _class = 'pill button left'))                
                else:
                    response.menubkn.append(A(cat.title.capitalize()+' ', _href = URL(r = request, f = 'index', args = cat.slug), _class = 'pill button middle'))
            
except Exception, e:
        raise HTTP(400, 'No hay categorías registradas: %s' % e)
