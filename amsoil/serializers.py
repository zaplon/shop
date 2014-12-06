from rest_framework import serializers
from amsoil.models import Product, Cart, CartProduct, ProductVariation, ShippingMethod, PaymentMethod

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod

class ProductVariationSerializer(serializers.ModelSerializer):
    attributesString = serializers.CharField(source='getAttributesString')
    class Meta:
        model = ProductVariation
        fields = ('id','price', 'attributesString',)

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='getMainImage', read_only=True)
    variations = ProductVariationSerializer()
    class Meta:
        model = Product
        fields = ('id','name','description','price','image', 'shortDescription','variations','categories',)

class CartProductSerializer(serializers.ModelSerializer):
    productVariation = ProductVariationSerializer()
    product = ProductSerializer()
    class Meta:
        model = CartProduct
        fields = ('productVariation', 'quantity', 'price', 'product',)


class CartSerializer(serializers.ModelSerializer):
    cartProducts = CartProductSerializer()
    class Meta:
        model = Cart
        fields = ('cartProducts',)
