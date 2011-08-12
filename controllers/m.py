# -*- coding: utf-8 -*-

def index():
    if request.args(0) == 'no':
        session.mobile = False
    else:
        session.mobile = True
    return redirect(URL(r=request,c='default',f='index'))
