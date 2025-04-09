from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet, AnswerViewSet, index, EditProfileView, ProfileView

router = DefaultRouter()
router.register('questions', QuestionViewSet, basename='question')
router.register('answers', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/edit/', EditProfileView.as_view(), name='edit-profile'),
    path('profile/', ProfileView.as_view(), name='edit-profile'),
]