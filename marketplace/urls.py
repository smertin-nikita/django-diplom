from rest_framework.routers import DefaultRouter

from marketplace.views import ReviewViewSet, ProductViewSet, CollectionViewSet, OrderViewSet

router = DefaultRouter()
router.register('review', ReviewViewSet, basename='review')
router.register('product', ProductViewSet, basename='product')
router.register('order', OrderViewSet, basename='order')
router.register('collection', CollectionViewSet, basename='collection')


urlpatterns = router.urls
