import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogPage(Handler):
    def render_mainblog(self, title="", error="",art="",arts=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC LIMIT 5")
        self.render("mainblog.html", title=title, art=art, arts=arts)

    def get(self):
        self.render_mainblog()

class MainPage(Handler):
    def render_mainblog(self, title="", error="",art="",arts=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC LIMIT 1 ")
        self.render("mainblog.html", title=title, art=art, arts=arts)

    def get(self):
        self.render_mainblog()



class PostPage(Handler):

    def render_newpost(self,title="",art="",error="") :
        self.render( "newpost.html",title=title, art=art, error=error)


    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            art = Art(title = title, art = art)
            art.put()
            id = art.key().id()
            self.redirect("/blog/%s" % id)
        else:
            error = "we need both title and art"
            self.render_newpost(title, art, error)

#class ViewPostHandler(webapp2.RequestHandler):
    #replace this with some code to handle the request
    #def get(self, id):
        #arts = Art.get_by_id(int(id))
        #self.render("mainblog.html", arts=arts)
class ViewPostHandler(Handler):

    def get(self, id):
        """ Render a page with post determined by the id (via the URL/permalink) """

        art = Art.get_by_id(int(id))
        if art:
            t = jinja_env.get_template("displaypost.html")
            response = t.render(art=art)
        else:
            error = "there is no post with id %s" % id
            t = jinja_env.get_template("404.html")
            response = t.render(error=error)

        self.response.out.write(response)




app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogPage),
    ('/blog/newpost', PostPage),
    (webapp2.Route('/blog/<id:\d+>', ViewPostHandler))
], debug=True)
