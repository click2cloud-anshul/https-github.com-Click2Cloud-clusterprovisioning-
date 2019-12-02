from django.conf.urls import url

from source_to_image import views

urlpatterns = [
    url(r'^s2i/create-image$', views.create_new_image_using_s2i),
    url(r'^s2i/get-image-details$', views.get_image_details),
    url(r'^s2i/delete-image$', views.delete_image_details)
]