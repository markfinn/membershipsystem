import os
from flask import Flask, render_template, request, redirect, current_app, abort
import ConfigParser
import stripe
from functools import wraps

def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if request.is_secure:
                return fn(*args, **kwargs)
        else:
                return redirect(request.url.replace("http://", "https://"))
        
        abort(500)
            
    return decorated_view


config = ConfigParser.SafeConfigParser()
config.read('settings.conf')

stripe_sk = config.get('stripe_keys', 'secret')
stripe_pk = config.get('stripe_keys', 'publishable')


assert stripe_sk[3:7] == stripe_pk[3:7]
assert stripe_sk[3:7] == 'test' or  stripe_sk[3:7] == 'live'
watermark=''
if stripe_sk[3:7] == 'test':
  watermark='TEST'

stripe.api_key = stripe_sk
        
app = Flask(__name__)

@app.route('/signup')
@ssl_required
def index():
    return render_template('signup.html', key=stripe_pk, watermark=watermark)

@app.route('/signup_result', methods=['POST'])
@ssl_required
def charge():

    if 'plan' not in request.form:
      plan=None
      description='no plan, but a customer account has been created.  Email the treasurer to continue with whatever you are doing.'
    else:
      try:
        plan = stripe.Plan.retrieve(request.form['plan'])
        description='%s at a recurring cost of $%d / %s'%(plan.name, plan.amount/100, plan.interval)
      except:
        return render_template('error.html', what='requested membership plan not found', watermark=watermark)

    try:
      customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['stripeToken'],
        plan=plan
        )
      if not plan:
        description += ' reference customer# %s'%customer.id
    except:
      return render_template('error.html', what='error adding new customer', watermark=watermark)

#    # Amount in cents
#    amount = 500
#    charge = stripe.Charge.create(
#        customer=customer.id,
#        amount=amount,
#        currency='usd',
#        description='Flask Charge'
#    )



    return render_template('signup_complete.html', description=description, watermark=watermark)

if __name__ == '__main__':
    app.run(debug=True)
