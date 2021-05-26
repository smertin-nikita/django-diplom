from rest_framework.routers import DefaultRouter

from marketplace.views import ReviewViewSet

router = DefaultRouter()
router.register('review', ReviewViewSet, basename='review')

urlpatterns = router.urls
