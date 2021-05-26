from rest_framework.routers import DefaultRouter

from marketplace.views import ReviewViewSet, ProductViewSet

router = DefaultRouter()
router.register('review', ReviewViewSet, basename='review')
router.register('product', ProductViewSet, basename='product')

urlpatterns = router.urls
