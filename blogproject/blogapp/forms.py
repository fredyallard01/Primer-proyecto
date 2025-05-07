from django import forms #Importa el módulo de formularios de Django, que proporciona herramientas para crear y manejar formularios HTML
from django.contrib.auth.forms import UserCreationForm #Importa el formulario predeterminado de Django para registrar nuevos usuarios. Este formulario ya incluye campos básicos como username, password1 y password2
from django.contrib.auth.models import User #Importa el modelo de usuario predeterminado de Django, que representa a los usuarios en la base de datos

class RegisterForm(UserCreationForm): #Define una nueva clase de formulario que hereda de UserCreationForm. Se  puede personalizar o ampliarlo
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User #Indica que este formulario está asociado con el modelo User. Esto significa que los datos ingresados en el formulario se pueden guardar directamente en una instancia del modelo User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2") #Especifica los campos que se incluirán en el formulario