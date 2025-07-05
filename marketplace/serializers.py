from rest_framework import serializers

from utils.image_service import ImageUploadService
from .models import Category, Product, ProductImage, Review, Cart, CartItem, Order, OrderItem, Wishlist
from authentication.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image_url', 'is_primary']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=None, allow_empty_file=False),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'seller': {'read_only': True},
        }

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = super().create(validated_data)
        
        if uploaded_images:
            upload_service = ImageUploadService()
            for i, image_file in enumerate(uploaded_images):
                is_primary = i == 0  # First image is primary
                image_url = upload_service.upload_product_image(
                    image_file=image_file,
                    product_id=str(product.id),
                    is_primary=is_primary
                )
                if image_url:
                    ProductImage.objects.create(
                        product=product,
                        image_url=image_url,
                        is_primary=is_primary
                    )
        
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = super().update(instance, validated_data)
        
        if uploaded_images:
            upload_service = ImageUploadService()
            for image_file in uploaded_images:
                image_url = upload_service.upload_product_image(
                    image_file=image_file,
                    product_id=str(product.id),
                    is_primary=False
                )
                if image_url:
                    ProductImage.objects.create(
                        product=product,
                        image_url=image_url,
                        is_primary=False
                    )
        
        return product


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'created_at', 'updated_at']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.items.count()
    
    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'total_amount', 'created_at', 'updated_at']

class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'products', 'created_at', 'updated_at']