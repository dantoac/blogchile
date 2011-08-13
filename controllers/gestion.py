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
    #nuevo_feed = LOAD(f = 'agregarFeed.load', ajax = True, ajax_trap = True,target='nuevo_feed')
    response.flash = XML('<img src="%s" /> Espera errores. Mientras estemos en Beta los feeds y/o categorias "podrian" ser succionados por el vortex maligno y perderse en el limbo... disculpa ;3' % URL(r=request,c='static',f='images',args=['warn.png']))
    #return dict(nuevo_feed = nuevo_feed, nueva_categoria = nueva_categoria,mensaje = msg)
    return dict(mensaje=msg)

@auth.requires_login()
def agregarFeed():
    msg = XML('Recuerda que el feed debe ser de un blog chileno (da lo mismo donde esté alojado el sitio, por si preguntas :P)')
    form = SQLFORM(db.feed, formstyle = 'divs', submit_button = 'agregar feed')
    if form.accepts(request, session):
        response.flash = 'has registrado un nuevo feed.'
        
    agregarFeed = DIV(msg,form)
    return dict(form = agregarFeed)

@auth.requires_login()
def agregarCategoria():
    nueva_categoria = SQLFORM(db.categoria, formstyle = 'divs', submit_button = 'agregar categoría')
    msgcat = XML('Considera que editaremos los nombres de las categorías que sean redundantes, ofensivas o perjudiquen la navegación en el sitio.')

    if nueva_categoria.accepts(request, session):
        response.flash = 'ha registrado una nueva categoría.'
        response.js = '$.modal.close();'

    nueva_categoria = DIV(msgcat,nueva_categoria)
    
    return dict(nueva_categoria = nueva_categoria)


@auth.requires(request.cid)
def misfeeds():
    fdata = db(db.feed.created_by == auth.user_id).select(db.feed.id,db.feed.title,db.feed.categoria,db.feed.is_active,orderby=~db.feed.id)
    misfeeds = TABLE(THEAD(TR(TH('Título'),TH('Categoría'),TH('Activado'))))
    for f in fdata:
        misfeeds.append(TR(TD(f.title),TD(f.categoria.title),TD(f.is_active),TH(A(SPAN(_class='icon pen'),'Editar',_href=URL(c='gestion',f='editarFeed.load',args=[f.id]),_class='negative button',cid='editarfeed'))))

    return dict(misfeeds=misfeeds)

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
