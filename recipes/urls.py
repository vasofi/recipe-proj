from django.contrib import admin
from django.urls import path
from recipes.views import RecipeView, FindRecipeView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('get-recipe/', FindRecipeView.as_view()),
    path('', RecipeView.as_view()),
    
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)