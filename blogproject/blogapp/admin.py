#Aquí podemos registrar diferentes models(data que se guarda en la database) para que así aparezca en nuestro panel de administración
from django.contrib import admin
from .models import Blog, Review, Comment

admin.site.register(Blog)
admin.site.register(Review)
admin.site.register(Comment)
