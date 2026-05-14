"""
Главный файл маршрутизации URL.

Здесь подключаются URL из всех приложений,
а также специальный URL для django-debug-toolbar.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Все URL нашего приложения clubs
    path('', include('clubs.urls')),

    # URL для debug_toolbar — только в режиме разработки
    path('__debug__/', include('debug_toolbar.urls')),
]
