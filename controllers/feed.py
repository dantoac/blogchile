

def fromrss():
    import gluon.contrib.feedparser as feedparser
    from gluon.tools import prettydate





    #===========================================================================
    # del response.headers['Cache-Control']
    # del response.headers['Pragma']
    # del response.headers['Expires']
    # response.headers['Cache-Control']='max-age=300'
    #===========================================================================


    # obteniendo el id, nombre y slug de las categorías registradas
    cats4menu = db(db.categoria.id > 0).select(db.categoria.id, db.categoria.nombre, db.categoria.slug)
    catslug = request.args(0) or cats4menu[0]['nombre'].lower()

    response.title = "%s: %s %s" % (request.application.upper(), request.function.capitalize(), catslug.capitalize())

    # formando el menú con las categorías existentes
    for cat in cats4menu:
        response.menu.append([cat.nombre.capitalize(), None, URL(r = request, args = cat.slug)])

    # obteniendo la petición de categoría desde la url, sino setea por defecto la primera conocida en db  


    # obteniendo los feeds categorizados bajo el slug solicitado desde la url 
    src_data = db((db.categoria.slug == catslug) & (db.feed_categoria.categoria == db.categoria.id) & (db.feed_categoria.feed == db.feed.id)).select()

    feedsrc = [] #creando una lista para guardar los feeds

    # obteniendo la url de cada feed bajo la categoría solicitada
    for data in src_data:
        feedsrc.append(data.feed.url) #guardamos cada url en una lista
        categoria_actual = data.categoria.nombre.capitalize()
    titulo = ''
    rss = {}
    articulos = DIV()
    rss_entries = []
    # obteniendo las url's de la lista de feeds y posibilitando su enumeración
    for fnum, src in enumerate(feedsrc):
        fnum = fnum + 1 # para que la enumeración comience en 1 y no en 0
        # obtenermos el feed de cada url de la [lista de feeds] guardándolo en la variable feed (:P)
        feed = feedparser.parse(src)
        #try:
        entradas = ''
        # seteando el título de cada feed y opcionalmente su enumeración y descripción
        titulo = XML(DIV("%(titulo_feed)s" % dict(feed_numero = fnum, titulo_feed = feed.channel.title), _class = 'feed_titulo'))
        descripcion = XML(DIV(feed.channel.description, _class = 'feed_meta feed_descripcion'))

        # antes de obtener las entradas de cada feed, resetamos el total máximo
        limite = 0



        # obteniedo las entradas de cada feed y posibilitando su enumeración
        for inum, i in enumerate(feed.entries):
            inum = inum + 1 # para que la enumeración comience en 1 y no en 0
            entradas += XML(DIV(A('%s.-' % inum, _name = '%(titulo_feed)s-%(num)s' % dict(titulo_feed = feed.channel.title, num = inum)), \
            A(i.title, _name = IS_SLUG.urlify(XML(i.title)), _href = URL(r = request, f = 'xlink', args = [catslug, IS_SLUG.urlify(XML(i.title))], vars = {'link':XML(i.link)}), _class = 'item_link'), \
            DIV(i.updated or '?', _class = 'feed_meta'), _class = 'feed_item'))

            db.noticia.update(title = i.title, slug = IS_SLUG.urlify(XML(i.title)), link = i.link, description = feed.channel.title, feed = data.feed.id, created_on = i.updated) or \
            db.noticia.insert(title = i.title, slug = IS_SLUG.urlify(XML(i.title)), link = i.link, description = feed.channel.title, feed = data.feed.id, created_on = i.updated)

            limite += 1 # acercando al límite!

            # límite máximo de feeds a obtener


            if limite == 3:
                break
        rss_entries.append(dict(title = i.title, link = 'http://' + request.env.http_host + URL(c = request.controller, f = request.function, args = [catslug + XML('#') + IS_SLUG.urlify(XML(i.title))], extension = False), description = feed.channel.title))


        articulos.append(DIV(XML(titulo + entradas), _class = 'feed_bloque izq'))


    if request.extension == 'rss':
        rss['title'] = request.application.upper()
        rss['link'] = request.url
        rss['description'] = 'Noticias de %s' % categoria_actual

        rss['entries'] = rss_entries

        contenido = rss
    else:
        contenido = dict(feeds = articulos,)
    return response.render(contenido)

def feedb():
    import gluon.contrib.feedparser as feedparser
    from gluon.tools import prettydate

    #===========================================================================
    # del response.headers['Cache-Control']
    # del response.headers['Pragma']
    # del response.headers['Expires']
    # response.headers['Cache-Control']='max-age=300'
    #===========================================================================


    # obteniendo el id, nombre y slug de las categorías registradas
    cats4menu = db(db.categoria.id > 0).select(db.categoria.id, db.categoria.nombre, db.categoria.slug)
    catslug = request.args(0) or cats4menu[0]['nombre'].lower()

    response.title = "%s: %s %s" % (request.application.upper(), request.function.capitalize(), catslug.capitalize())

    # formando el menú con las categorías existentes
    for cat in cats4menu:
        response.menu.append([cat.nombre.capitalize(), None, URL(r = request, args = cat.slug)])

    # obteniendo la petición de categoría desde la url, sino setea por defecto la primera conocida en db  


    # obteniendo los feeds categorizados bajo el slug solicitado desde la url 
    src_data = db((db.categoria.slug == catslug)
                  & (db.feed_categoria.categoria == db.categoria.id)
                  & (db.feed_categoria.feed == db.feed.id)
                  ).select()


    feedsrc = [] #creando una lista para guardar los feeds

    # obteniendo la url de cada feed bajo la categoría solicitada
    for data in src_data:
        feedsrc.append(data.feed.url) #guardamos cada url en una lista
        categoria_actual = data.categoria.nombre.capitalize()

    entry_titulo = entry_link = entry_description = titulo = '';rss = {};articulos = DIV();rss_entries = []

    # obteniendo las url's de la lista de feeds y posibilitando su enumeración
    for fnum, src_url in enumerate(feedsrc):
        fnum = fnum + 1 # para que la enumeración comience en 1 y no en 0
        # obtenermos el feed de cada url de la [lista de feeds] guardándolo en la variable feed (:P)
        #feed = feedparser.parse(src)
        feed_data = db((db.noticia.feed == db.feed.id) & (db.feed.url == src_url)
                       ).select(db.noticia.ALL, orderby = ~db.noticia.created_on)

        #try:
        entradas = ''
        # seteando el título de cada feed y opcionalmente su enumeración y descripción
        titulo = XML(DIV("%(titulo_feed)s" % dict(feed_numero = fnum, titulo_feed = data.feed.nombre), _class = 'feed_titulo'))
        descripcion = XML(DIV(data.feed.descripcion, _class = 'feed_meta feed_descripcion'))

        # antes de obtener las entradas de cada feed, resetamos el total máximo
        limite = 0

        # obteniedo las entradas de cada feed y posibilitando su enumeración
        for inum, i in enumerate(feed_data):
            inum = inum + 1 # para que la enumeración comience en 1 y no en 0
            entradas += XML(DIV(A('%s.-' % inum, _name = '%(titulo_feed)s-%(num)s' % dict(titulo_feed = data.feed.nombre, num = inum)), \
            A(i.title, _name = IS_SLUG.urlify(XML(i.title)), _href = URL(r = request, f = 'xlink', args = [catslug, IS_SLUG.urlify(XML(i.title))], vars = {'link':XML(i.link)}), _class = 'item_link'), \
            DIV(prettydate(i.created_on, T) or '?', _class = 'feed_meta'), _class = 'feed_item'))

            #db.noticia.update(title = i.title, slug = IS_SLUG.urlify(XML(i.title)), link = i.link, description = feed.channel.title, feed = data.feed.id, created_on = i.updated) or \
            #db.noticia.insert(title = i.title, slug = IS_SLUG.urlify(XML(i.title)), link = i.link, description = feed.channel.title, feed = data.feed.id, created_on = i.updated)

            limite += 1 # acercando al límite!

            # límite máximo de feeds a obtener


            #if limite == 3:
            #    break


            '''
            rss_entries.append(dict(title = i.title, link = 'http: // ' + request.env.http_host \
                                    + URL(c = request.controller, f = request.function, \
                                          args = [catslug + XML('#') + IS_SLUG.urlify(XML(i.title))], \
                                          extension = False), description = i.description))
            '''
            entry_title = i.title
            entry_link = "http://' + request.env.http_host \
                                + URL(c = request.controller, f = request.function, \
                                      args = [catslug + XML('#') + IS_SLUG.urlify(XML(i.title))]"
            entry_description = i.description




            rss_entries.append(dict(title = entry_title, link = entry_link, description = entry_description))
        articulos.append(DIV(XML(titulo + entradas), _class = 'feed_bloque izq'))


    if request.extension == 'rss':
        rss['title'] = request.application.upper()
        rss['link'] = request.url
        rss['description'] = 'Noticias de %s' % categoria_actual

        rss['entries'] = rss_entries

        contenido = rss
    else:
        contenido = dict(feeds = articulos,)
    return response.render(contenido)
