import cherrypy
import os


class HelloWorld(object):

    @cherrypy.expose
    def index(self):
        return "Hello world!"



if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'error_page.404': os.path.join(os.path.abspath(os.getcwd()), "static/404.html")
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static',
            'tools.staticdir.index': "index.html"
        },
        

    }
    cherrypy.quickstart(HelloWorld(),'/',conf)
