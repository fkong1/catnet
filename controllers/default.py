# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

@auth.requires_login()
def story():
    logger.info('The session is: %r' % session)
    story = None
    if auth.user is not None:
        story = db( (db.story.is_public)).select()
    else:
        story = db(db.story.is_public is True).select(db.story.ALL)
        logger.info(story)
    return dict(story=story)

@auth.requires_login()
def experience():
    return dict()

@auth.requires_login()
def shop():
    loginurl = auth.settings.login_url + '?_next=' + auth.settings.login_next
    return dict(message=T('Welcome to web2py!'),loginurl=loginurl)

@auth.requires_login()
def adoption():
    logger.info('The session is: %r' % session)

    catInfor = None
    if auth.user is not None:
        catInfor = db((db.catInfor.is_available)).select()
    else:
        catInfor = db(db.catInfor.is_available is True).select(db.catInfor.ALL)
        logger.info(catInfor)
    return dict(catInfor = catInfor)


def no_swearing_adoption(form):
    if 'shit' in form.vars.catInfor:
        form.errors.catInfor = T('No swearing please')


def no_swearing(form):
    if 'shit' in form.vars.story:
        form.errors.story = T('No swearing please')

def add():
    """adds a story."""
    form = SQLFORM(db.story)
    if form.process(onvalidation=no_swearing).accepted:
        session.flash = T("Checklist added.")
        redirect(URL('default', 'story'))
    elif form.errors:
        session.flash = T('Please correct the info')
    return dict(form=form)

@auth.requires_login()
@auth.requires_signature()
def delete():
    if request.args(0) is not None:
        q = ((db.story.user_email == auth.user.email)&
             (db.story.id == request.args(0)))
        db(q).delete()
    redirect(URL('default', 'story'))

@auth.requires_login()
def edit():
    if request.args(0) is None:
        redirect(URL('default', 'story'))
    else:
        q = ((db.story.user_email == auth.user.email)&
             (db.story.id == request.args(0)))
        cl = db(q).select().first()
        if cl is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'story'))
        form = SQLFORM(db.story, record=cl, deletable=False)
        if form.process(onvalidation=no_swearing).accepted:
            session.flash = T('story edited.')
            redirect(URL('default', 'story'))
        elif form.errors:
            session.flash = T('Please enter correct values.')
    return dict(form=form)

def toggle_public():
    if request.args(0) is not None :
        q = ((db.story.user_email == auth.user.email) &
             (db.story.id == request.args(0)))
        row = db(q).select().first()
        if row.is_public == True:
            row.update_record(is_public = False)
        else:
            row.update_record(is_public = True)
    redirect(URL('default', 'story'))

def addcat():
    """Adds a catInfor."""
    form = SQLFORM(db.catInfor)
    if form.process(onvalidation = no_swearing_adoption).accepted:
        session.flash = T("catInfor added.")
        redirect(URL('default','adoption'))
    elif form.errors:
        session.flash = T('Please correct the info')
    return dict(form = form)

@auth.requires_login()
def toggle_available():
    if request.args(0) is not None:
        q = ((db.catInfor.user_email == auth.user.email) &
             (db.catInfor.id == request.args(0)))
        cl = db(q).select().first()
        if cl.is_available is True:
            cl.update_record(is_available = False)
        else:
            cl.update_record(is_available = True)
        redirect(URL('default', 'adoption'))

@auth.requires_login()
def editcat():
    if request.args(0) is None:
        redirect(URL('default', 'adoption'))
    else:
        q = ((db.catInfor.user_email == auth.user.email)&
             (db.catInfor.id == request.args(0)))
        cl = db(q).select().first()
        if cl is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'adoption'))

        url = URL('download')
        form = SQLFORM(db.catInfor, record=cl, upload=url)

        if form.process(onvalidation=no_swearing_adoption).accepted:
            session.flash = T('catInfor viewcat.')
            redirect(URL('default', 'adoption'))
        elif form.errors:
            session.flash = T('Please enter correct values.')
        return dict(form=form)

@auth.requires_login()
def viewcat():
    if request.args(0) is None:
        redirect(URL('default', 'adoption'))
    else:
        q =(db.catInfor.id == request.args(0))
        cl = db(q).select().first()
        if cl is None:
            session.flash = T('Not Authorized')
            redirect(URL('default','adoption'))

        url = URL('download')
        form = SQLFORM(db.catInfor, record=cl, upload=url, deletable=False, readonly=True,writable=False)
        #lat1=db(db.catInfor.id == cl).select(db.catInfor.lat)
        #lng1 = db(db.catInfor.id == cl).select(db.catInfor.lng)


        if form.process(onvalidation = no_swearing_adoption).accepted:
            session.flash = T('catInfor viewcat.')
            redirect(URL('default','adoption'))
        elif form.errors:
            session.flash = T('Please enter correct values.')
        return dict(form = form)



@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


