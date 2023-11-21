from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.create_project, name='create_project'),
    path('', views.project_list, name='projects'),
    path('<int:id>', views.project_details, name='project_details'),
    path('update/<int:id>', views.update_project, name='update_project'),
    path('delete/<int:id>', views.delete_project, name='delete_project'),
    path('report/<int:id>/', views.report_project, name='report_project'),
    path('donate/<int:id>', views.donate, name='donate'),
    path('search/', views.search_results, name='search_results'),
    path('categories/<int:category_id>', views.category_projects, name='category_projects'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('report_comment/<int:comment_id>/', views.report_comment, name='report_comment'),
    path('trigger-error/', views.trigger_server_error, name='trigger_server_error'),
]
