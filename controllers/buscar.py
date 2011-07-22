# -*- coding: utf-8 -*-


response.meta.title = 'Buscando en Blogs Chilenos'
response.meta.description = 'Buscando entre los artículo y publicaciones de la blogósfera chilena'

def index():
    
    form = FORM(INPUT(_name='q'),INPUT(_type='submit', _value='Buscar'))
    if form.accepts(request.vars,session):
        redirect(URL(c='buscar',f='index',vars={'q':request.post_vars.q}))    

    return dict(form=form)

#@auth.requires(request.cid)
def buscar():

    redirect(URL(c='default',f='index'))

    response.title = 'Buscar publicaciones en blogs chilenos.'

    ads_busqueda = XML('''
<script type="text/javascript"><!--
google_ad_client = "ca-pub-9647318851151478";
/* ads en resultado de búsqueda */
google_ad_slot = "3282677144";
google_ad_width = 468;
google_ad_height = 60;
//-->
</script>
<script type="text/javascript"
src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>
''')

    form = FORM('Buscar Publicación', INPUT(_name='buscando', requires=IS_LENGTH(minsize=6,error_message='Intenta especificar más tu búsqueda.')),INPUT(_type='submit'))
    lista_resultados = ''
    if form.accepts(request.post_vars):

        buscado = XML(form.vars.buscando)
        buscado = buscado.split()
        try:
            for patron in buscado:
                #resultados = db((db.noticia.title.contains(patron)) | (db.noticia.description.contains(patron))
                resultados = db((db.noticia.title.contains(patron))).select(db.noticia.id,db.noticia.title, db.noticia.created_on, db.noticia.slug,db.noticia.feed, orderby=~db.noticia.id, distinct=True)


            #lista_resultados = TABLE(THEAD(TR(TH('Resultados'))), _id='search_results')
            lista_resultados = UL( _id='search_results')
            for n,resultado in enumerate(resultados):
                n=n+1

                title = A(resultado.title.capitalize(),_href=URL(f='go',args=[resultado.slug,resultado.id]),_target='new')

                #body = nltk.util.clean_html(XML(resultado.description))+'(...)'
                meta = 'Obtenido el %(fecha)s desde %(fuente)s' % dict(fuente=A(resultado.feed.title, _href=resultado.feed.source, _target='_blank'), fecha = str(resultado.created_on))
                
                #lista_resultados.append(TR(TD(XML('%(meta)s <br />%(title)s<br />%(ads)s' % dict(title=title,meta=meta,ads = ads_busqueda)),_class='title'),_class='search_result'))
                lista_resultados.append(LI(SPAN(XML('%(meta)s <br />%(title)s<br />%(ads)s' % dict(title=title,meta=meta,ads = ads_busqueda)),_class='title'),_class='search_result'))

            response.flash = 'Encontré %s resultado(s).' % n
            #response.flash = 'Mostrando los últimos 100 artículos'
        except Exception,e:
            #response.flash = e
            response.flash = 'No encontré artículos con esas palabras. Intenta usando el buscador de google que está más arriba.'
            lista_resultados = XML(SPAN('Sin Resultados', _class='error'))
    return dict(form=form,lista_resultados=lista_resultados)
