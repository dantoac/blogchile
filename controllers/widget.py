# -*- coding: utf-8 -*-
def indicadoreseconomicos():
    import urllib2
    import locale

    locale.setlocale(locale.LC_NUMERIC, 'es_CL.UTF8')
    uri = 'http://www.averigualo.cl/feed/indicadores.xml'
    
    try:
        pag = urllib2.urlopen(uri).read()

        html = TAG(pag)

        #eurocalculado = float(html.element('dolar')[0].replace(',','.')) / float(html.element('euro')[0].replace(',','.'))
        eurocalculado = locale.atof(html.element('dolar')[0]) / locale.atof(html.element('euro')[0])
        dolarcalculado = locale.atof(html.element('dolar')[0])
        ufcalculado = locale.atof(html.element('uf')[0])

        html_indicadores = DIV(B('UF: $%(uf)s | Dólar: $%(dolar)s | Euro: $%(euro)s' % dict(uf=str(ufcalculado)[:8],dolar=str(dolarcalculado)[:6],euro=str(eurocalculado)[:6])), _class='der', _id='indicadoreseconomicos')

        #html_indicadores = XML(IMG(_src=URL(c='static',f='images/indicadoreseconomicos.png'),_class='izq'))+H2('Indicadores Económicos')+html_indicadores

    except Exception,e:
        html_indicadores = DIV('error: No pude obtener los indicadores económicos. %s' % e, _class='error')
    return dict(indicadores=XML(html_indicadores))

def obtienedatos(urllugar,ubicacion):
    import urllib2
    import time
    import datetime
    import urllib 

    ubicacion = ubicacion.capitalize()

    #import unicodedata as ud

    session.forget()

    #url = urllib.urlencode(urllugar)

    
    url = urllib.quote_plus(urllugar,safe='?&/=:')
    #response.flash = url
    resp = urllib2.urlopen(str(XML(url)))

    xmlstr = resp.read()
    #xmlstr = xmlstr.decode('utf-8','ignore')

    # eliminando el xml que no podemos parsear
    xmlstr = xmlstr.replace('<![CDATA[','')
    xmlstr = xmlstr.replace(']]>','')

    # web2pyando el xml :D
    html = TAG(xmlstr)

    # obteniendo los datos para hoy
    ahora_temp = XML(html.element('temp_c')[0])
    ahora_icono = html.element('weathericonurl')[0]
    lugar = html.element('query')[0]
    ahora_velocidad_viento = html.element('windspeedkmph')[0]
    ahora_humedad = html.element('humidity')[0]
    ahora_tempMax = html.element('tempmaxc')[0] 
    ahora_tempMin = html.element('tempminc')[0]
    ahora_fecha = html.element('date')[0]


    # empaquetando el bloque de los indicadores de temperatura en una variable
    temp_info = UL(LI('Actual: %s °C' % ahora_temp),LI('Máxima: %s °C ' % ahora_tempMax),LI('Mínima: %s °C' % ahora_tempMin),_class='temperaturas')

    # formando el mensaje completo
    infohoy = DIV(_id='ahora')
    infohoy.append(XML('%(lugar)s  %(icono)s  %(temp)s' % dict(
        temp=temp_info,
        lugar=H2(lugar,_class='lugar_nombre'),
        icono = IMG(_src=ahora_icono,_class='ahora_icono'),)
                       )
                   )

    
    # obteniendo el pronóstico
    #pronostico = TABLE(THEAD(TH('Próximos días:')), _id='proximosdias')
    pronostico = DIV(SPAN(ubicacion,_class='dia'),_class='pronostico')
    
    for t in html.elements('weather'):
        icono = IMG(_src=t.element('weathericonurl')[0],_class='icono')
        #lugar = t.element('query')[0]
        #velocidad_viento = t.element('windspeedkmph')[0]
        #humedad = t.element('humidity')[0]
        tempMax = t.element('tempmaxc')[0] 
        tempMin = t.element('tempminc')[0]
        fecha = t.element('date')[0]
        
        facs = time.strptime(fecha, '%Y-%m-%d')
        fecha_dt = datetime.date(facs[0],facs[1],facs[2])
        fecha_str = XML(fecha_dt.strftime('%A').capitalize()[:2])
        
        #pronostico.append(TR(TD('%s' % fecha_str),TD('Min.: %s°C' % tempMin),TD('Max.:%s°C' % tempMax),TD(XML('%s' % icono)),_class='pronostico_diario')) #dict(icono=icono,fecha=fecha_str,tempMax=tempMax,tempMin=tempMin)),_id=fecha,_class='pronostico_diario'))

        pronostico.append(SPAN(icono,B(fecha_str),': %(tempMin)s/%(tempMax)s°C ' % dict(tempMax=tempMax,tempMin=tempMin)))
                        

    

    #msg = DIV(infohoy,pronostico,_class='tiempo_local')
    msg = pronostico

    
    return XML(msg)

def pronosticotiempo():
    key = '9e6119ed3a211314113107'

    lugares = ['arica','iquique','antofagasta','copiapó','la serena','valparaíso','viña del mar','santiago','rancagua','talca','chillán','concepción','temuco','valdivia','puerto montt','coyhaique','punta arenas','robinson crusoe','hanga roa']

    lugares.sort()
       
    tiempo = ''
    for lugar in lugares:
        try:
            #tiempo += obtienedatos(lugar)
            url = XML('http://free.worldweatheronline.com/feed/weather.ashx?q=%(lugar)s,chile&format=xml&num_of_days=5&key=%(key)s' % dict(key=key,lugar=lugar))
            url2 = URL(scheme='http',host='free.worldweatheronline.com',a='feed',f='weather.ashx',vars={'q':lugar,'format':'xml','num_of_days':'5','key':key})

            tiempo += obtienedatos(url,lugar)
        except Exception,e:
            tiempo = DIV('%s' % e, _class='error')

    response.js = 'jQuery(document).ready(function(){jQuery("#tiempo").cycle({fx:"scrollHorz",timeout:"3000",continuous:0,speed:9000});});'
    #response.js = 'jQuery("#tiempo").cycle({fx:"scrollHorz",timeout:"3000",continuous:0,speed:9000});'

    return dict(message=XML(tiempo))
