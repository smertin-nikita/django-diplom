from rest_framework.routers import DefaultRouter

from marketplace.views import ReviewViewSet, ProductViewSet, CollectionViewSet, OrderViewSet

router = DefaultRouter()
router.register('product-reviews', ReviewViewSet, basename='product-reviews')
router.register('products', ProductViewSet, basename='products')
router.register('orders', OrderViewSet, basename='orders')
router.register('product-collections', CollectionViewSet, basename='product-collections')


urlpatterns = router.urls
