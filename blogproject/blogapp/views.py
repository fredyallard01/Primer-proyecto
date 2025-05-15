from django.shortcuts import redirect, render #Redirige a una URL especifica
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from blogapp import models
from .models import Blog, Review, Comment, UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin #Restringe el acceso a usuarios autenticados
from django.contrib.auth.models import User
from .forms import RegisterForm
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile



class BlogListView(ListView):
    model = Blog
    template_name = 'blogapp/blog_list.html'

    def get_queryset(self):
        genre = self.request.GET.get('genre')

        if genre:
            return Blog.objects.filter(genre=genre).annotate(average_rating=Avg('reviews__rating'))
        
        return Blog.objects.all().annotate(average_rating=Avg('reviews__rating'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['genres'] = Blog.GAMES_GENRES

        context['top_rated_blogs'] = Blog.objects.annotate(
            average_rating=Avg('reviews__rating')
        ).order_by('-average_rating')[:5]

        context['most_commented_blogs'] = Blog.objects.annotate(
            comment_count=Count('reviews__comments'),
            average_rating=Avg('reviews__rating')
        ).order_by('-comment_count')[:5]

        return context

class BlogDetailView(DetailView): #Muestra los detalles de un blog específico
    model = Blog
    template_name = 'blogapp/blog_detail.html'

    def get_queryset(self):
        return Blog.objects.all().annotate(average_rating=Avg('reviews__rating'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.object
        context['average_rating'] = blog.reviews.aggregate(Avg('rating'))['rating__avg']
        return context

class BlogCreateView(LoginRequiredMixin, CreateView): #Permite a un usuario autenticado crear un nuevo blog
    model = Blog
    fields = ['genre','title', 'content',] #Campos del formulario (title, content)
    template_name = 'blog_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.object.pk})



class ReviewCreateView(LoginRequiredMixin, CreateView): #Permite a un usuario autenticado crear una reseña para un blog
    model = Review
    fields = ['rating', 'comment']
    template_name = 'blogapp/review_form.html'

    def dispatch(self, request, *args, **kwargs): #Verifica si el usuario ya ha escrito una reseña para el blog. Si es así, muestra un mensaje de error y redirige al detalle del blog
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        blog_id = self.kwargs['pk']
        user = request.user

        if Review.objects.filter(blog_id=blog_id, reviewer=user).exists():
            messages.error(request, "Ya has escrito una reseña para este blog.")
            return redirect('blogapp:blog_detail', pk=blog_id)

        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form): #Asigna el usuario autenticado como autor del comentario y lo enlaza a la reseña correspondiente
        form.instance.reviewer = self.request.user
        form.instance.blog_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self): #Redirige al detalle del blog tras crear el comentario
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['pk']})


class CommentCreateView(LoginRequiredMixin,CreateView): #Permite a un usuario autenticado agregar un comentario a una reseña
    model = Comment
    fields = ['content']
    template_name = 'blogapp/comment_form.html'

    def form_valid(self, form):
        form.instance.commenter = self.request.user
        form.instance.review_id = self.kwargs['review_pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blogapp:blog_detail', kwargs={'pk': self.kwargs['blog_pk']})


class RegisterView(CreateView): #Permite a un usuario registrarse en la aplicación
    form_class = RegisterForm
    template_name = 'blogapp/register.html'
    success_url = '/login/'

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    template_name = 'blogapp/edit_profile.html'
    success_url = '/profile/edit'

    def get_object(self):
        return self.request.user 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        if form.is_valid():
            form.save()

            profile, _ = UserProfile.objects.get_or_create(user=self.object)
            if 'profile-photo' in request.FILES:
                profile.profile_picture = request.FILES['profile-photo']
                profile.save()

            return redirect(self.success_url)

        return self.form_invalid(form)
    
class AdminDashboardView(View):
    def get(self, request):
        if not request.user.is_staff:
            return redirect('blogapp:blog_list')

        total_blogs = Blog.objects.count()
        blogs_by_genre = Blog.objects.values('genre').annotate(count=Count('id'))
        total_reviews = Review.objects.count()
        total_comments = Comment.objects.count()

        context = {
            'total_blogs': total_blogs,
            'blogs_by_genre': blogs_by_genre,
            'total_reviews': total_reviews,
            'total_comments': total_comments
        }

        return render(request, 'blogapp/admin_dashboard.html', context)
    

@csrf_exempt  # Puedes quitar esto si usas correctamente el CSRF token
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        image = request.FILES['upload']
        path = default_storage.save(f'uploads/{image.name}', ContentFile(image.read()))
        image_url = default_storage.url(path)
        return JsonResponse({'url': image_url})
    return JsonResponse({'error': 'Upload failed'}, status=400)