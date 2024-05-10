from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Product, OrderDetail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt 
from django.http import JsonResponse, HttpResponseNotFound
import stripe, json

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, "myapp/index.html", {'products': products})


def detail(request, id):
    product = Product.objects.get(id=id)
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    return render(request, "myapp/detail.html", {'product': product, 'stripe_publishable_key': stripe_publishable_key})


@csrf_exempt
def create_checkout_session(request,id):
    request_data = json.loads(request.body)
    product = Product.objects.get(id=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Create a PaymentIntent
    payment_intent = stripe.PaymentIntent.create(
        amount=int(product.price * 100),  # Amount in cents
        currency='usd',
        metadata={'integration_check': 'accept_a_payment'},
    )
    
    checkout_session = stripe.checkout.Session.create(
        customer_email = request_data['email'],
        payment_method_types = ['card'],
        line_items=[
            {
                'price_data':{
                    'currency':'usd',
                    'product_data':{
                        'name':product.name,
                    },
                    'unit_amount':int(product.price * 100)
                },
                'quantity':1,
            }
        ],
        mode='payment',
        success_url = request.build_absolute_uri(reverse('success')) +
        "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_uri(reverse('failed')),
        
    )
    
    # Create an OrderDetail instance
    order = OrderDetail.objects.create(
        customer_email=request_data['email'],
        product=product,
        stripe_payment_intent=payment_intent.id,
        amount=int(product.price),
    )
    
    order.save()
    
    return JsonResponse({'sessionId':checkout_session.id})


def payment_success_view(request):
    session_id = request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    payment_intent_id = session.payment_intent
    order = get_object_or_404(OrderDetail,stripe_payment_intent= payment_intent_id)
    order.has_paid=True
    order.save()
    
    return render(request,'myapp/payment_success.html',{'order':order})


def payment_failed_view(request):
    return render(request, "myapp/payment_failed.html")