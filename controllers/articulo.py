
def index():
    if request.args:
        pag = URL(c='plugin_wiki',f='page.html',args=request.args(0))
        return redirect(pag)
    
    return redirect(URL(c='default',f='index'))
