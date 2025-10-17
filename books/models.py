from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import requests
from django.conf import settings
from django.core.exceptions import ValidationError


class Book(models.Model):
    
    title = models.CharField(max_length=200, verbose_name="Título")
    author = models.CharField(max_length=100, verbose_name="Autor")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    
    # Información de precios
    cost_usd = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Costo en USD"
    )
    selling_price_local = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Precio de Venta Local"
    )
    local_currency = models.CharField(max_length=3, default='VES', verbose_name="Moneda Local")
    
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Cantidad en Stock")
    
    category = models.CharField(max_length=100, verbose_name="Categoría")
    supplier_country = models.CharField(max_length=2, verbose_name="País del Proveedor")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} - {self.author}"
    
    def clean(self):
        """Validación personalizada del modelo"""
        if self.stock_quantity < 0:
            raise ValidationError({'stock_quantity': 'La cantidad en stock no puede ser negativa.'})
        
        if self.cost_usd <= 0:
            raise ValidationError({'cost_usd': 'El costo en USD debe ser mayor a 0.'})
    
    def calculate_suggested_price(self, target_currency=None):
        """Calcula el precio de venta sugerido basado en el costo USD y margen"""
        if target_currency is None:
            target_currency = self.local_currency
            
        margin = Decimal('0.40')
        suggested_price_usd = Decimal(str(self.cost_usd)) * (Decimal('1') + margin)
        
        suggested_price_local = self.convert_currency(suggested_price_usd, 'USD', target_currency)
        
        return suggested_price_local
    
    def convert_currency(self, amount, from_currency, to_currency):
        """Convierte monedas usando una API de tasas de cambio REAL"""
        if from_currency == to_currency:
            return amount
        
        try:
            # Usar la API REAL de tasas de cambio
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            rates = response.json()['rates']
            if to_currency in rates:
                return Decimal(str(amount)) * Decimal(str(rates[to_currency]))
            else:
                print(f"⚠️ ADVERTENCIA: Moneda {to_currency} no encontrada en API. Usando tasa 1:1")
                return Decimal(str(amount))
                
        except (requests.RequestException, KeyError, ValueError) as e:
            print(f"⚠️ ERROR: No se pudo obtener tasa de cambio: {str(e)}")
            print(f"⚠️ Usando tasa 1:1 como respaldo")
            return Decimal(str(amount))
    
    def _get_fallback_rate(self, amount, from_currency, to_currency):
        """Tasas de cambio fijas como respaldo - SOLO PARA CASOS DE EMERGENCIA"""
        return Decimal(str(amount))
    
    def is_low_stock(self, threshold=10):
        """Verifica si el stock está por debajo del umbral especificado"""
        return self.stock_quantity <= threshold
    
    def update_suggested_price(self):
        """Actualiza el precio sugerido y lo guarda"""
        self.selling_price_local = self.calculate_suggested_price()
        self.save(update_fields=['selling_price_local', 'updated_at'])
    
    def calculate_price_detailed(self, target_currency=None):
        """Calcula el precio con información detallada del proceso"""
        if target_currency is None:
            target_currency = self.local_currency
            
        exchange_rate = self.get_exchange_rate('USD', target_currency)
        
        cost_local = Decimal(str(self.cost_usd)) * exchange_rate
        
        # Aplicar margen del 40%
        margin_percentage = 40
        selling_price_local = cost_local * Decimal('1.40')
        
        return {
            'book_id': self.id,
            'cost_usd': float(self.cost_usd),
            'exchange_rate': float(exchange_rate),
            'cost_local': float(cost_local),
            'margin_percentage': margin_percentage,
            'selling_price_local': float(selling_price_local),
            'currency': target_currency,
            'calculation_timestamp': self.updated_at.isoformat()
        }
    
    def get_exchange_rate(self, from_currency, to_currency):
        """Obtiene la tasa de cambio actual"""
        if from_currency == to_currency:
            return Decimal('1.0')
            
        try:
            # Usar la API de tasas de cambio
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            rates = response.json()['rates']
            if to_currency in rates:
                return Decimal(str(rates[to_currency]))
            else:
                return self._get_fallback_rate(Decimal('1.0'), from_currency, to_currency)
                
        except (requests.RequestException, KeyError, ValueError):
            return self._get_fallback_rate(Decimal('1.0'), from_currency, to_currency)
    
    def save(self, *args, **kwargs):
        """Override del método save para calcular precio sugerido automáticamente"""
        if not self.selling_price_local:
            self.selling_price_local = self.calculate_suggested_price()
        
        super().save(*args, **kwargs)


class PriceHistory(models.Model):
    """Historial de cambios de precios para análisis"""
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='price_history')
    cost_usd = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price_local = models.DecimalField(max_digits=10, decimal_places=2)
    exchange_rate_used = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Precios"
        verbose_name_plural = "Historial de Precios"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.book.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
