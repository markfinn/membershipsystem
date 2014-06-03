import os
from flask import Flask, render_template, request
import ConfigParser
import stripe


config = ConfigParser.SafeConfigParser()
config.read('settings.conf')

stripe.api_key = config.get('stripe_keys', 'secret')
        
app = Flask(__name__)

@app.route('/signup')
def index():
    return render_template('signup.html', key=config.get('stripe_keys', 'publishable'))

@app.route('/signup_result', methods=['POST'])
def charge():

    if 'plan' not in request.form:
      plan=None
      description='no plan, but a customer account has been created.  Email the treasurer to continue with whatever you are doing.'
    else:
      try:
        plan = stripe.Plan.retrieve(request.form['plan'])
        description='%s at a recurring cost of $%d / %s'%(plan.name, plan.amount/100, plan.interval)
      except:
        return render_template('error.html', what='requested membership plan not found')

    try:
      customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['stripeToken'],
        plan=plan
        )
      if not plan:
        description += ' reference customer# %s'%customer.id
    except:
      return render_template('error.html', what='error adding new customer')

#    # Amount in cents
#    amount = 500
#    charge = stripe.Charge.create(
#        customer=customer.id,
#        amount=amount,
#        currency='usd',
#        description='Flask Charge'
#    )



    return render_template('signup_complete.html', description=description)

if __name__ == '__main__':
    app.run(debug=True)
