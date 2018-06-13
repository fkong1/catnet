# Here go your api methods.
import json
import traceback

def user():
    return response.json(auth.user)

@auth.requires_login()
def get_userlist():
    q = (db.auth_user.id != auth.user.id)

    user_list = db(q).select(db.auth_user.id,db.auth_user.first_name,orderby=db.auth_user.id)

    return response.json(dict(user_list=user_list))

@auth.requires_login()
def get_user_images():
    if request.args(0) is not None:
        q = (db.user_images.created_by == request.args(0))

        user_images = db(q).select(orderby=~db.user_images.created_on,limitby=(0,20))

        return response.json(dict(user_images=user_images))
    return response.json(dict())

@auth.requires_login()
def add_image():
    if not request.vars.get('imageurl'):
        return response.json(dict(result=False,msg='bad image url'))
    if not request.vars.get('price'):
        return response.json(dict(result=False,msg='bad price'))
    person_id=db.user_images.insert(created_by=auth.user.id,image_url=request.vars['imageurl'],price=request.vars['price'])
    q = (db.user_images.created_by == auth.user.id)

    user_images = db(q).select(orderby=~db.user_images.created_on,limitby=(0,20))
    return response.json(dict(result=True,msg='add image success',user_images=user_images))

@auth.requires_login()
def set_price():
    if request.args(0) is None:
        return response.json({'result':False,'msg':'no id'})
    if not request.vars.get('price'):
        return response.json(dict(result=False,msg='bad price'))
    q = (db.user_images.id == request.args(0))
    cl = db(q).select().first()
    if cl is None:
        return response.json({'result':False,'msg':'no image'})
    cl.price = request.vars['price']
    cl.update_record()
    return response.json({'result':True,'msg':'price edited.','obj':cl})

@auth.requires_login()
def purchase():
    """Ajax function called when a customer orders and pays for the cart."""
    if not URL.verify(request, hmac_key=session.hmac_key):
        raise HTTP(500)
    # Creates the charge.
    import stripe
    # Your secret key.
    stripe.api_key = myconf.get('stripe.private_key')
    token = json.loads(request.vars.transaction_token)
    amount = float(request.vars.amount)
    try:
        charge = stripe.Charge.create(
            amount=int(amount * 100),
            currency="usd",
            source=token['id'],
            description="Purchase",
        )
    except stripe.error.CardError as e:
        logger.info("The card has been declined.")
        logger.info("%r" % traceback.format_exc())
        return "nok"
    except Exception as e:
        print(e)
        return "nok"
    db.customer_order.insert(
        customer_info=request.vars.customer_info,
        transaction_token=json.dumps(token),
        cart=request.vars.cart)
    return "ok"
