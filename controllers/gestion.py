# -*- coding: utf-8 -*-
@auth.requires_membership('admin')
def index():

    return locals()

def core():
    return locals()

def personal():

    return locals()
@auth.requires(request.cid)
def agregar():
    msg = ''
    nuevo_feed = LOAD(f = 'agregarFeed.load', ajax = True, ajax_trap = True,target='nuevo_feed')
    response.flash = '<img src="%s" /> Espera errores. Mientras estemos en Beta los feeds y/o categorias "podrian" ser succionados por el vortex maligno y perderse en el limbo... disculpa ;3' % URL(r=request,c='static',f='images',args=['warn.png'])
    #if auth.has_membership('user_1'):
    #    nueva_categoria = LOAD(c = 'gestion', f = 'agregarCategoria.load', ajax = True,target='nueva_categoria')
    #else:
    #    nueva_categoria = 'Aún no tienes autorización para agregar categorías.'
    nueva_categoria = LOAD(c = 'gestion', f = 'agregarCategoria.load', ajax = True,target='nueva_categoria')

    #if form.accepts(request, session):
    #   response.flash = 'ha registrado una nueva categoría.'
    #    response.js = '$.modal.close();'

    #categorizando = LOAD(f = 'categorizando.load', ajax = False, ajax_trap = True)

    return dict(nuevo_feed = nuevo_feed, nueva_categoria = nueva_categoria,mensaje = msg)

@auth.requires_login()
def agregarFeed():
    msg = 'Recuerda que el feed debe ser de un blog chileno (da lo mismo donde esté alojado el sitio, por si preguntas :P)'
    form = SQLFORM(db.feed, formstyle = 'divs', submit_button = 'agregar feed')
    if form.accepts(request, session):
        response.flash = 'has registrado un nuevo feed.'
        
    agregarFeed = DIV(msg,form)
    return dict(form = agregarFeed)

@auth.requires(request.cid)
def agregarCategoria():
    nueva_categoria = SQLFORM(db.categoria, formstyle = 'divs', submit_button = 'agregar categoría')
    msgcat = 'Considera que editaremos los nombres de las categorías que sean redundantes, ofensivas o perjudiquen la navegación en el sitio.'

    if nueva_categoria.accepts(request, session):
        response.flash = 'ha registrado una nueva categoría.'
        response.js = '$.modal.close();'

    nueva_categoria = DIV(msgcat,nueva_categoria)
    
    return dict(nueva_categoria = nueva_categoria)
