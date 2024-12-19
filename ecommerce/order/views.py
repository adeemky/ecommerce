from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from .permissions import IsAuthenticatedAndOrderOwner


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedAndOrderOwner]

    def get_queryset(self):

        return Order.objects.filter(user=self.request.user)
