from rest_framework import serializers
from amsoil.models import Product, Cart, CartProduct, ProductVariation, ShippingMethod, PaymentMethod, NewsletterReceiver,\
    Attribute, Order

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod

class ProductVariationSerializer(serializers.ModelSerializer):
    attributesString = serializers.CharField(source='getAttributesString',read_only=True)
    name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ProductVariation
        fields = ('product', 'name', 'attributesString', 'id', 'price','amount',)

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='getMainImage', read_only=True)
    variations = serializers.CharField(source='getVariations', read_only=True)
    hasManyVariations = serializers.BooleanField(read_only=True)
    variationsDetails = serializers.CharField(source='getVariationsDetails', read_only=True)
    groupedAttributes = serializers.CharField(source='getGroupedAttributes', read_only=True)
    class Meta:
        model = Product
        fields = ('id','name','description','price','image', 'shortDescription','categories', 'variations',
                  'hasManyVariations', 'variationsDetails','groupedAttributes')

class CartProductSerializer(serializers.ModelSerializer):
    productVariation = ProductVariationSerializer()
    product = ProductSerializer()
    class Meta:
        model = CartProduct
        fields = ('quantity', 'price','product','productVariation',)


class CartSerializer(serializers.ModelSerializer):
    cartProducts = CartProductSerializer(many=True)
    class Meta:
        model = Cart
        fields = ('cartProducts',)


class NewsletterReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterReceiver




class ShopAttributeSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source='group.name', read_only=True)
    class Meta:
        model = Attribute
        fields = ('id','name','group')

class ShopProductVariationSerializer(serializers.ModelSerializer):
    attributes = ShopAttributeSerializer(many=True, read_only=True)
    class Meta:
        model = ProductVariation
        fields = ('id', 'price','amount','image','attributes')

class ShopProductSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='getMainImage', read_only=True)
    variations = ShopProductVariationSerializer(many=True, read_only=True)
    grouped_variations = serializers.CharField(source='getVariations', read_only=True)

    class Meta:
        model = Product
        fields = ('id','name','image','shortDescription','categories', 'variations','grouped_variations',
                  'hasManyVariations')



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
