from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Review
from orders.models import OrderItem

@login_required
def submit_review(request, product_id):
    """Submit product review"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user purchased the product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()
    
    if not has_purchased:
        messages.warning(request, 'You can only review products you have purchased.')
        return redirect('products:product_detail', product_id=product_id)
    
    # Check if already reviewed
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    
    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '').strip()
        
        if not comment:
            messages.error(request, 'Please write a review comment.')
            return redirect('reviews:submit_review', product_id=product_id)
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, 'Review updated successfully!')
        else:
            # Create new review
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
            messages.success(request, 'Thank you for your review!')
        
        return redirect('products:product_detail', product_id=product_id)
    
    context = {
        'product': product,
        'existing_review': existing_review,
    }
    return render(request, 'reviews/submit_review.html', context)