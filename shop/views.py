import json
import logging
import time

import stripe
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
# from django.urls import reverse
from django.views.generic import View

from .models import Book

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        start_time = time.time()
        logger.info(f"User({request.user.id}) posted.")
        queryset = Book.objects.select_related('publisher').prefetch_related(
            'authors').order_by('publish_date')
        keyword = request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
        context = {
            'keyword': keyword,
            'book_list': queryset,
        }
        logger.debug(f"Finished in {time.time() - start_time:.2f} sec.")
        return TemplateResponse(request, 'shop/book_list.html', context)


index = IndexView.as_view()


class DetailView(LoginRequiredMixin, View):
    def get(self, request, book_id, *args, **kwargs):
        book = get_object_or_404(Book, pk=book_id)

        # Charges API（旧API）を利用した場合
        # session = stripe.checkout.Session.create(
        #     payment_method_types=['card'],
        #     line_items=[{
        #         'price_data': {
        #             'product': 'prod_JrHxyqQP0vTHeR',
        #             'unit_amount': book.price,
        #             'currency': 'jpy',
        #         },
        #         'quantity': 1,
        #     }],
        #     mode='payment',
        #     success_url=request.build_absolute_uri(reverse('shop:complete')),
        #     cancel_url=request.build_absolute_uri(reverse('shop:detail', args=(book_id,))),
        # )
        context = {
            'book': book,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            # 'checkout_session_id': session.id,
        }
        return TemplateResponse(request, 'shop/book_detail.html', context)


detail = DetailView.as_view()


class CreatePaymentAjaxView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body.decode())
        book_id = body.get('item', {}).get('id')
        book = get_object_or_404(Book, pk=book_id)

        intent = stripe.PaymentIntent.create(
            amount=book.price,
            currency='jpy'
        )
        return JsonResponse({
            'clientSecret': intent['client_secret']
        })


payment = CreatePaymentAjaxView.as_view()

# class CompleteView(LoginRequiredMixin, View):
#     def get(self, request, *args, **kwargs):
#         return TemplateResponse(request, 'shop/book_detail.html')
#
#
# complete = CompleteView.as_view()
