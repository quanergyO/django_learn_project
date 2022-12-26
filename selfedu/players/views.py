import os.path

from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from .forms import AddPostForm, RegisterUserForm, LoginUserForm, ContactForm
from .models import *
from .serializers import PlayerSerializer
from .utils import DataMixin


class PlayersHome(DataMixin, ListView):
    model = Player
    template_name = 'players/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница')
        context = dict(list(context.items()) + list(c_def.items()))
        return context

    def get_queryset(self):
        return Player.objects.filter(is_published=True).select_related('cat')


# def index(request):
#     posts = Player.objects.all()
#
#     context = {
#         'posts': posts,
#         'title': 'Главная страница',
#         'cat_selected': 0,
#     }
#     return render(request, 'players/index.html', context=context)


def about(request):
    return render(request, 'players/about.html', {'title': 'О сайте'})


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'players/addpage.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавление статьи')
        context = dict(list(context.items()) + list(c_def.items()))
        return context


# def addpage(request):
#     if request.method == 'POST':
#         form = AddPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = AddPostForm()
#     return render(request, 'players/addpage.html', {'form': form, 'title': 'Добавление статьи'})

class ContactFormView(DataMixin, FormView):
    form_class = ContactForm
    template_name = 'players/contact.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Обратная связь')
        context = dict(list(context.items()) + list(c_def.items()))
        return context

    def form_valid(self, form):
        print(form.cleaned_date)
        return redirect('home')


class ShowPost(DataMixin, DetailView):
    model = Player
    template_name = 'players/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['post'])
        context = dict(list(context.items()) + list(c_def.items()))
        return context


# def show_post(request, post_slug):
#     post = get_object_or_404(Player, pk=post_slug)
#
#     context = {
#         'post': post,
#         'title': post.title,
#         'cat_selected': post.cat_id,
#     }
#
#     return render(request, 'players/post.html', context=context)


class PlayersCategory(DataMixin, ListView):
    model = Player
    template_name = 'players/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Player.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория' + str(c.name), cat_selected=c.pk)
        context = dict(list(context.items()) + list(c_def.items()))
        return context


# def show_category(request, cat_id):
#     posts = Player.objects.filter(cat_id=cat_id)
#
#     if len(posts) == 0:
#         raise Http404()
#
#     context = {
#         'posts': posts,
#         'title': 'Отображение по рубрикам',
#         'cat_selected': cat_id,
#     }
#     return render(request, 'players/index.html', context=context)

class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'players/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        context = dict(list(context.items()) + list(c_def.items()))
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'players/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        context = dict(list(context.items()) + list(c_def.items()))
        return context

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')


def pageNotFound(request, exception):
    return HttpResponseNotFound('Страница не найдена')


class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')

        if not pk:
            return Player.objects.all()[:3]

        return Player.objects.filter(pk=pk)

    @action(methods=['get'], detail=True)
    def category(self, request, pk=None):
        cats = Category.objects.get(pk=pk)
        return Response({'cats': cats.name})


class PlayerAPIList(generics.ListCreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerAPIView(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class PlayerAPIViewV2(APIView):
    def get(self, request):
        p = Player.objects.all()
        return Response({'posts': PlayerSerializer(p, many=True).data})

    def post(self, request):
        serializer = PlayerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'post': serializer.data})

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "Method PUT not allowed"})

        try:
            instance = Player.objects.get(pk=pk)
        except:
            return Response({"error": "Object does not exists"})

        serializer = PlayerSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'post': serializer.data})

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({"error": "Method DELETE not allowed"})

        try:
            instance = Player.objects.get(pk=pk)
        except:
            return Response({"error": "Object does not exists"})

        instance.delete()

        return Response({"post": "delete post" + str(pk)})


