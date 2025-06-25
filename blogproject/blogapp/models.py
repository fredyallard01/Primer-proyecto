#De aquí se provee la data que se presenta en el sitio web
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# MODELOS

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Blog(models.Model): #Representa una entrada de blog
    GAMES_GENRES = [
        ('ACCION', 'Acción'),
        ('AVENTURA', 'Aventura'),
        ('ESTRATEGIA', 'Estrategia'),
        ('RPG', 'RPG'),
        ('SIMULADOR', 'Simulador'),
        ('DEPORTES', 'Deportes'),
        ('PUZZLES', 'Puzzles'),
        ('SANDBOX', 'Sandbox'),
        ('ARCADE', 'Arcade'),
        ('MOBA', 'MOBA'),
        ('SHOOTER', 'Shooter'),
        ('JUEGOS_MUSICALES', 'Juegos Musicales'),
        ('SUPERVIVENCIAS', 'Supervivencias'),
        ('SOULSLIKE', 'Soulslike'),
    ]
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE) # Relación con el modelo User (autor del blog). Si el usuario es eliminado, los blogs asociados también se eliminan (on_delete=models.CASCADE).
    created_at = models.DateTimeField(auto_now_add=True)
    genre = models.CharField(max_length=20, choices=GAMES_GENRES)

    def __str__(self):
        return self.title


class Review(models.Model): #Representa una reseña de un blog
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'reviewer')

    def __str__(self):
        return f"{self.reviewer.username} - {self.blog.title}"



class Comment(models.Model): #Representa un comentario en una reseña.

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter.username}"