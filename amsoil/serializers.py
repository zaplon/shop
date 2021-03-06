from rest_framework import serializers
from amsoil.models import *

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


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class ShopAttributeSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source='group.name', read_only=True)
    for_variations = serializers.BooleanField(source='group.forProductVariations', read_only=True)
    class Meta:
        model = Attribute
        fields = ('id','name','group', 'for_variations')

class ShopProductVariationSerializer(serializers.ModelSerializer):
    attributes = ShopAttributeSerializer(many=True, read_only=True)
    class Meta:
        model = ProductVariation
        fields = ('id', 'price','amount','image','attributes')

class ShopProductSerializer(serializers.ModelSerializer):
    attributes = ShopAttributeSerializer(many=True, read_only=True)
    image = serializers.CharField(source='getMainImage', read_only=True)
    variations = ShopProductVariationSerializer(many=True, read_only=True)
    grouped_variations = serializers.CharField(source='getVariations', read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'image', 'shortDescription','categories', 'variations', 'grouped_variations',
                  'hasManyVariations', 'attributes')



class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice


class OrderSerializer(serializers.ModelSerializer):
    cart = CartSerializer()
    paymentMethod = PaymentMethodSerializer()
    shipment = ShipmentSerializer(many=True, read_only=True)
    shippingMethod = ShippingMethodSerializer()
    invoice = InvoiceSerializer()
    user = ClientSerializer()
    class Meta:
        model = Order
        fields = ('date', 'email', 'total', 'cart', 'get_status', 'id', 'number','shipment', 'discount',
        'paymentMethod', 'shippingMethod', 'invoice', 'user')
