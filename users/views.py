from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework.exceptions import NotAcceptable

from orders.models import Order, OrderProducts
from products.models import Product
from .serializers import UserSerializer
from .models import User
from .permissions import IsAccountOwnerOrAdmin

from drf_spectacular.utils import extend_schema

import uuid

@extend_schema(
    summary="List and create users",
    description="This endpoint allows you to list all users and create new ones.",
    tags=["List and Create Users"]
)

class UserView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
            if self.request.method =='POST':
                return [AllowAny()]
            return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return User.objects.all()
        else: 
            user_id = self.request.user.id
            return queryset.filter(id=user_id)
        

@extend_schema(
    summary="Retrieve, update and delete a user",
    description="This endpoint allows you to retrieve, update and delete a specific user.",
    tags=["Retrieve, update and delete a user"]
)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAccountOwnerOrAdmin]

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_destroy(self, instance):
        user = User.objects.filter(id=self.kwargs['pk']).first()

        found_in_done = Order.objects.filter(user_id=self.kwargs["pk"]).filter(order_status="PEDIDO REALIZADO").first()
        found_in_progress = Order.objects.filter(user_id=self.kwargs["pk"]).filter(order_status="EM ANDAMENTO").first()
        found_in_delivered = Order.objects.filter(user_id=self.kwargs["pk"]).filter(order_status="ENTREGUE").first()

        if user.is_seller:
            if found_in_done or found_in_progress:
                raise NotAcceptable({"message": "This user has unfinished orders."})
            products = Product.objects.filter(seller_id=user.id)
            if products:
                for product in products:
                    orders = OrderProducts.objects.filter(product_id=product.id)
                    for order in orders:
                        in_started_order = Order.objects.filter(id=order.id).filter(order_status="PEDIDO REALIZADO").first()
                        in_progress_order = Order.objects.filter(id=order.id).filter(order_status="PEDIDO REALIZADO").first()

                        if in_started_order or in_progress_order:
                            raise NotAcceptable({"message": "This seller has in progress orders."})
                        else:
                            product.stock = 0
                            product.availability = False
                            product.save()

                            user.is_active = False
                            user.save()
         
        elif found_in_done or found_in_progress:
            raise NotAcceptable({"message": "This user has unfinished orders."})
        elif found_in_delivered:
            user = User.objects.get(id=self.kwargs['pk'])
            user.is_active = False
            user.save()
        else:
            return super().perform_destroy(instance)


class UserActivateView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAccountOwnerOrAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.is_active = True
        instance.save()
