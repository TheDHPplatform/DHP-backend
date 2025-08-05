from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage, Review, Cart, CartItem, Order, OrderItem, Wishlist
from .serializers import (
    AddCartItemSerializer, CategorySerializer, ProductSerializer, ProductImageSerializer,
    ReviewSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer, ToggleProductSerializer, WishlistSerializer
)
from .filters import ProductFilter
from rest_framework.parsers import MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            queryset = queryset.all()
        else:
            queryset = queryset.prefetch_related('products').filter(products__isnull=False).distinct()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def populated_categories(self, request):
        categories = Category.objects.prefetch_related('products').all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related('images')
    # parser_classes = [MultiPartParser]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    # def get_parsers(self):
    #     if getattr(self, 'swagger_fake_view', False):
    #         return []
    #     return super().get_parsers()

    def perform_create(self, serializer):
        product = serializer.save(seller=self.request.user)
    #     # Handle uploaded images directly
    #     # uploaded_images = self.request.get('uploaded_images')  # Retrieve images from the request
    #     for i, image_file in enumerate(uploaded_images):
    #         is_primary = i == 0  # First image will be primary
    #         ProductImage.objects.create(
    #             product=product,
    #             image=image_file,
    #             is_primary=is_primary
    #         )
    
    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Review.objects.none()
        return Review.objects.filter(user=user)
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Cart.objects.none()
        if user.is_staff or user.is_superuser:
            return Cart.objects.all()
        return Cart.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @extend_schema(
        request=AddCartItemSerializer,
        responses={200: CartSerializer},
        description="Add an item to the user's cart."
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if product.stock < quantity:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()
        
        product.stock -= int(quantity)
        product.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Order.objects.none()

        return Order.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create order logic here
        # This would typically involve:
        # 1. Creating the order
        # 2. Creating order items from cart items
        # 3. Calculating total
        # 4. Processing payment
        # 5. Clearing cart
        
        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)
    
class ToggleProductResponseSerializer(serializers.Serializer):
    added = serializers.BooleanField()
    product_id = serializers.IntegerField()


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user)
        
    @extend_schema(
        request=ToggleProductSerializer,
        responses={200: ToggleProductResponseSerializer},
        description="Toggle a product in the user's wishlist (add or remove)."
    )
    @action(detail=False, methods=['post'])
    def toggle_product(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        if product in wishlist.products.all():
            wishlist.products.remove(product)
            added = False
        else:
            wishlist.products.add(product)
            added = True
        
        return Response({'added': added, 'product_id': product_id})