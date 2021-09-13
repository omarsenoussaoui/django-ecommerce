from store.forms import ReviewForm
from django.http import HttpResponse
from django.shortcuts import redirect, render , get_object_or_404

from carts.models import CartItem
from carts.views import _cart_id
from .models import Product, ProductGallery, ReviewRating
from category.models import *
from django.core.paginator import EmptyPage , Paginator, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages , auth

# Create your views here.

def store(request , category_slug = None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category ,slug =category_slug)
        products = Product.objects.filter(category = categories , is_availble = True )
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_availble = True).order_by('id')
        product_count = products.count()
    paginator = Paginator(products, 2)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
    context = {
        'products' : paged_product,
        'product_count': product_count,
    }
    return render(request , 'store/store.html' , context )


def product_detail(request,category_slug, product_slug):
    
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug = product_slug )
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request) , product = single_product).exists()
    except Exception as e :
        raise e

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'reviews': reviews,
        'product_gallery':product_gallery,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword))
        product_count = products.count()
        context = {
            'products' : products,
            'product_count':product_count,
        }
        return render(request,'store/store.html',context)



def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
