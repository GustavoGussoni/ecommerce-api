from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from addresses.permissions import IsAccountOwnerOrAdmin

from .models import Cart
from .serializers import CartSerializer, CartClearSerializer


class CartView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    lookup_field = 'product_id'
    serializer_class = CartSerializer

    def get_object(self):
        return Cart.objects.get(user=self.request.user)
    
    def perform_update(self, serializer):
        products = self.kwargs.get('product_id')
        if not products:
            raise NotFound()

        quantity = self.request.data
        serializer.save(user=self.request.user, products=products, context=quantity)


class CartClearView(generics.UpdateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartClearSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAccountOwnerOrAdmin]
    lookup_field = 'id'

