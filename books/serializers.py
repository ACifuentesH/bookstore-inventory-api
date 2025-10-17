from rest_framework import serializers
from .models import Book, PriceHistory


class BookSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Book"""
    
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'isbn',
            'cost_usd',
            'selling_price_local',
            'local_currency',
            'stock_quantity',
            'category',
            'supplier_country',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_cost_usd(self, value):
        """Validar que el costo en USD sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El costo en USD debe ser mayor a 0.")
        return value
    
    def validate_stock_quantity(self, value):
        """Validar que la cantidad en stock no sea negativa"""
        if value < 0:
            raise serializers.ValidationError("La cantidad en stock no puede ser negativa.")
        return value
    
    def validate_isbn(self, value):
        """Validar formato básico del ISBN"""
        # Remover guiones y espacios
        isbn_clean = value.replace('-', '').replace(' ', '')
        
        # Verificar que solo contenga dígitos y X (para ISBN-10)
        if not isbn_clean.replace('X', '').isdigit():
            raise serializers.ValidationError("El ISBN debe contener solo dígitos y X.")
        
        # Verificar longitud (ISBN-10 o ISBN-13)
        if len(isbn_clean) not in [10, 13]:
            raise serializers.ValidationError("El ISBN debe tener 10 o 13 dígitos.")
        
        return value


class BookCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear libros (sin precio sugerido automático)"""
    
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'isbn',
            'cost_usd',
            'local_currency',
            'stock_quantity',
            'category',
            'supplier_country'
        ]
    
    def create(self, validated_data):
        """Crear libro y calcular precio sugerido automáticamente"""
        book = Book.objects.create(**validated_data)
        # El precio sugerido se calcula automáticamente en el método save() del modelo
        return book


class BookUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar libros"""
    
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'isbn',
            'cost_usd',
            'selling_price_local',
            'local_currency',
            'stock_quantity',
            'category',
            'supplier_country'
        ]
    
    def update(self, instance, validated_data):
        """Actualizar libro y recalcular precio si cambió el costo"""
        old_cost = instance.cost_usd
        instance = super().update(instance, validated_data)
        
        # Si cambió el costo, recalcular el precio sugerido
        if old_cost != instance.cost_usd:
            instance.update_suggested_price()
        
        return instance


class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer para el historial de precios"""
    
    class Meta:
        model = PriceHistory
        fields = [
            'id',
            'book',
            'cost_usd',
            'selling_price_local',
            'exchange_rate_used',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BookListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar libros"""
    
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'isbn',
            'cost_usd',
            'selling_price_local',
            'local_currency',
            'stock_quantity',
            'category',
            'supplier_country'
        ]
