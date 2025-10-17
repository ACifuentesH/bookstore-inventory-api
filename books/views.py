from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from .models import Book, PriceHistory
from .serializers import (
    BookSerializer, 
    BookCreateSerializer, 
    BookUpdateSerializer,
    BookListSerializer,
    PriceHistorySerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para la API"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear libros"""
    queryset = Book.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'supplier_country']
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'author', 'cost_usd', 'stock_quantity', 'created_at']
    ordering = ['title']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookCreateSerializer
        return BookListSerializer


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un libro específico"""
    queryset = Book.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookUpdateSerializer
        return BookSerializer


@api_view(['GET'])
def book_search_by_category(request):
    """Buscar libros por categoría"""
    category = request.GET.get('category', '')
    
    if not category:
        return Response(
            {'error': 'El parámetro category es requerido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    books = Book.objects.filter(category__icontains=category)
    serializer = BookListSerializer(books, many=True)
    
    return Response({
        'count': books.count(),
        'results': serializer.data
    })


@api_view(['GET'])
def low_stock_books(request):
    """Obtener libros con stock bajo"""
    threshold = request.GET.get('threshold', 10)
    
    try:
        threshold = int(threshold)
    except ValueError:
        return Response(
            {'error': 'El threshold debe ser un número entero'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    books = Book.objects.filter(stock_quantity__lte=threshold)
    serializer = BookListSerializer(books, many=True)
    
    return Response({
        'threshold': threshold,
        'count': books.count(),
        'results': serializer.data
    })


@api_view(['POST'])
def calculate_price(request, book_id):
    """Calcular precio de venta sugerido con integración externa"""
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {'error': 'Libro no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Validar que el costo USD sea mayor a 0
    if book.cost_usd <= 0:
        return Response(
            {'error': 'El costo en USD debe ser mayor a 0'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Obtener moneda objetivo del request o usar la del libro
        target_currency = request.data.get('currency', book.local_currency)
        
        # Calcular precio con información detallada
        calculation_result = book.calculate_price_detailed(target_currency)
        
        # Actualizar el precio en la base de datos
        book.selling_price_local = calculation_result['selling_price_local']
        book.local_currency = target_currency
        book.save(update_fields=['selling_price_local', 'local_currency', 'updated_at'])
        
        # Crear entrada en el historial
        PriceHistory.objects.create(
            book=book,
            cost_usd=book.cost_usd,
            selling_price_local=book.selling_price_local,
            exchange_rate_used=calculation_result['exchange_rate']
        )
        
        return Response(calculation_result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al calcular el precio: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def update_price(request, book_id):
    """Actualizar precio de un libro específico (endpoint legacy)"""
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {'error': 'Libro no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Recalcular precio sugerido
    book.update_suggested_price()
    
    # Crear entrada en el historial
    PriceHistory.objects.create(
        book=book,
        cost_usd=book.cost_usd,
        selling_price_local=book.selling_price_local
    )
    
    serializer = BookSerializer(book)
    return Response({
        'message': 'Precio actualizado exitosamente',
        'book': serializer.data
    })


@api_view(['GET'])
def price_history(request, book_id):
    """Obtener historial de precios de un libro"""
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response(
            {'error': 'Libro no encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    history = PriceHistory.objects.filter(book=book).order_by('-created_at')
    serializer = PriceHistorySerializer(history, many=True)
    
    return Response({
        'book': BookSerializer(book).data,
        'price_history': serializer.data
    })


@api_view(['GET'])
def exchange_rate_info(request):
    """Obtener información sobre las tasas de cambio actuales"""
    try:
        import requests
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return Response({
            'base_currency': data['base'],
            'date': data['date'],
            'rates': {
                'VES': data['rates'].get('VES', 'No disponible'),
                'EUR': data['rates'].get('EUR', 'No disponible'),
                'GBP': data['rates'].get('GBP', 'No disponible'),
            }
        })
    except Exception as e:
        return Response(
            {'error': f'No se pudo obtener la información de tasas de cambio: {str(e)}'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
