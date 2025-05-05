from django.shortcuts import redirect #Redirige a una URL especifica
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Blog, Review, Comment
from django.contrib.auth.mixins import LoginRequiredMixin #Restringe el acceso a usuarios autenticados
from django.contrib.auth.models import User
from .forms import RegisterForm
from django.contrib import messages
from django.db.models import Avg



class BlogListView(ListView): #Muestra una lista de blogs
    model = Blog #Modelo asociado
    template_name = 'blogapp/blog_list.html' #Se especifica la plantilla HTML guardada en (blogapp/blog_list.html)


class BlogDetailView(DetailView): #Muestra los detalles de un blog específico
    model = Blog
    template_name = 'blogapp/blog_detail.html'

    def get_queryset(self):
        return Blog.objects.all().annotate(average_rating=Avg('reviews__rating'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.object
        average_rating = blog.reviews.aggregate(Avg('rating'))['rating__avg']
        context['average_rating'] = average_rating
        return context

class BlogCreateView(LoginRequiredMixin, CreateView): #Permite a un usuario autenticado crear un nuevo blog
    model = Blog
    fields = ['title', 'content'] #Campos del formulario (title, content)
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
    success_url = reverse_lazy('blogapp/login')

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

class ProfileEditView(LoginRequiredMixin,UpdateView): #Permite a un usuario autenticado editar su perfil
    model = User
    fields = ['username','first_name','last_name','email']
    template_name = 'blogapp/edit_profile.html'
    success_url = '/profile/edit'

    def get_object(self): #Devuelve el usuario autenticado actual para editar su perfil
        return self.request.user