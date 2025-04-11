from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
from django.shortcuts import render
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

def index(request):
    return render(request,"website/home.html")
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")

        if not username or not password or not email:
            return Response({"error": "Tous les champs sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Ce nom d'utilisateur existe déjà."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        return Response({"message": "Utilisateur créé avec succès."}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Nom d'utilisateur et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return Response({"error": "Mot de passe incorrect."}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all().order_by('-created_at')
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def upvote(self, request, pk=None):
        question = self.get_object()
        question.upvotes += 1
        question.save()
        return Response({"message": "Question upvoted", "upvotes": question.upvotes})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def downvote(self, request, pk=None):
        question = self.get_object()
        question.downvotes += 1
        question.save()
        return Response({"message": "Question downvoted", "downvotes": question.downvotes})


    def destroy(self, request, *args, **kwargs):
        question = self.get_object()
        if question.author != request.user:
            raise PermissionDenied("Vous ne pouvez supprimer que vos propres questions.")
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Suppression de la question effectuée avec succès."}, status=200)


class AnswerViewSet(ModelViewSet):
    queryset = Answer.objects.all().order_by('-created_at')
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def upvote(self, request, pk=None):
        answer = self.get_object()
        answer.upvotes += 1
        answer.save()
        return Response({"message": "Réponse upvotée", "upvotes": answer.upvotes})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def downvote(self, request, pk=None):
        answer = self.get_object()
        answer.downvotes += 1
        answer.save()
        return Response({"message": "Réponse downvotée", "downvotes": answer.downvotes})


    def destroy(self, request, *args, **kwargs):
        answer = self.get_object()
        if answer.author != request.user:
            raise PermissionDenied("Vous ne pouvez supprimer que vos propres réponses.")
        super().destroy(request, *args, **kwargs)
        return Response({"message": "Suppression de la réponse effectuée avec succès."}, status=200)

class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        username = request.data.get("username", user.username)
        email = request.data.get("email", user.email)
        password = request.data.get("password", None)

        if User.objects.filter(username=username).exclude(id=user.id).exists():
            return Response({"error": "Ce nom d'utilisateur est déjà utilisé."}, status=status.HTTP_400_BAD_REQUEST)

        user.username = username
        user.email = email

        if password:
            user.set_password(password)

        user.save()
        return Response({"message": "Profil mis à jour avec succès."}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
            "is_active": user.is_active
        }, status=status.HTTP_200_OK)