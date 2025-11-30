# attendance/urls.py
from django.conf import settings
from django.conf.urls.static import static
# from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import UserLoginView, HomeView, DashboardView, UserRegistrationView, CreateTopicView, TopicDetailView, TopicUpdateView, TopicDeleteView, MyView, GenerateQRCodeView, SubmitAttendanceView, StopAttendanceView, download_topic_details_as_csv, download_all_topics_and_entries_as_csv, AddManualEntryView, reorder_topics
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('create_topic/', CreateTopicView.as_view(), name='create_topic'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
     path('topic/update/<int:pk>/', TopicUpdateView.as_view(), name='update_topic'),
    path('topic/delete/<int:pk>/', TopicDeleteView.as_view(), name='delete_topic'),
    path('my-view/', MyView.as_view(), name='my_view'),
    path('topic/<int:topic_id>/', TopicDetailView.as_view(), name='topic_detail'),
    path('attendance/<int:topic_id>/generate-qr/', GenerateQRCodeView.as_view(), name='generate_qr_code'),
    path('attendance/<int:topic_id>/submit_attendance/', SubmitAttendanceView.as_view(), name='submit_attendance'),
    path('attendance/<int:topic_id>/stop/', StopAttendanceView.as_view(), name='stop_attendance'),
    path('qr/', views.qr_code_view, name='qr_code'),
    path('attendance/<int:topic_id>/download-csv/', download_topic_details_as_csv, name='download_topic_details_as_csv'),
    path('download-all-topics/', download_all_topics_and_entries_as_csv, name='download_all_topics'),
    path('topic/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('attendance/<int:topic_id>/add_manual_entry/', AddManualEntryView.as_view(), name='add_manual_entry'),
    path('reorder_topics/', reorder_topics, name='reorder_topics'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
