from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/search/', views.book_search_by_category, name='book-search-category'),
    path('books/low-stock/', views.low_stock_books, name='low-stock-books'),
    path('books/<int:book_id>/calculate-price/', views.calculate_price, name='calculate-price'),
    path('books/<int:book_id>/update-price/', views.update_price, name='update-price'),
    path('books/<int:book_id>/price-history/', views.price_history, name='price-history'),
    path('exchange-rates/', views.exchange_rate_info, name='exchange-rates'),
]
