from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail
from django.shortcuts import get_object_or_404
from .models import Cart, CartProducts
from products.serializers import ProductInCartSerializer
from products.models import Product


class CartSerializer(serializers.ModelSerializer):
    # products = ProductInCartSerializer(many=True)
    class Meta:
        model = Cart
        fields = ['id', 'total_price', 'items', 'products']
        read_only_fields = ['id']
        depth = 1

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        products = representation['products']
        cart = instance
        updated_products = []
        for product_data in products:
            product_id = product_data['id']
            product = Product.objects.get(id=product_id)
            product_data['quantity'] = ProductInCartSerializer(product, context={'cart': cart}).data['quantity']
            updated_products.append(product_data)
        representation['products'] = updated_products
        for product in representation['products']:
            product.pop('stock', None)
            product.pop('availability', None)
        return representation

    def create(self, validated_data: dict) -> Cart:
        return Cart.objects.create(**validated_data)

    def update(self, instance, validated_data):
        product = get_object_or_404(Product, id=int(validated_data['products']))

        quantity = validated_data['context']['quantity']

        found_product = CartProducts.objects.filter(cart_id=instance.id).filter(product_id=product).first()

        if found_product:
            found_product.quantity += quantity
            if found_product.quantity <= 0:
                found_product.delete()
            else:
                found_product.save()
        else:
            instance.products.add(product)
            product_in_cart = CartProducts.objects.filter(cart_id=instance.id).filter(product_id=product).first()
            product_in_cart.quantity = quantity
            product_in_cart.save()
        
        price = 0
        items = 0
        for item in instance.cartproducts_set.all():
            price += item.quantity * item.product.price
            items += item.quantity

        instance.total_price = price
        instance.items = items
        instance.save()

        return instance


class CartClearSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ['id', 'total_price', 'items', 'products']
        read_only_fields = ['id']
        depth = 1

    def update(self, instance, validated_data):
        instance.products.clear()
        instance.total_price = 0
        instance.items = 0
        instance.save()

        return instance
