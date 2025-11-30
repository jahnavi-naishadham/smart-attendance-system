# attendance/views.py
import base64
import io
import uuid
import time
import csv
from django.http import HttpResponse
from django.utils.text import slugify
from io import StringIO
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.utils import timezone
from rest_framework import generics, permissions
# from rest_framework.response import Response
# from rest_framework import status
from .models import Event, Attendance, QRCode
from .serializers import EventSerializer, AttendanceSerializer, QRCodeSerializer
from .utils import is_within_range, generate_qr_code, get_client_ip, is_same_subnet
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Topic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from .models import Topic
from .forms import TopicForm, AttendanceEntryForm
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
# attendance/views.py
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .utils import generate_qr_code
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest
import qrcode
from io import BytesIO
from django.views.generic import View
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from .models import AttendanceEntry


# from django.shortcuts import render
# from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import Topic
from django.http import HttpResponseForbidden
from datetime import timedelta, datetime
from django.shortcuts import render
from django.views.generic import View
# from django_qrcode.views import QRCodeView
from .models import Topic
from .models import AttendanceEntry

class GenerateQRCodeView(View):
    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        timestamp = int(timezone.now().timestamp())
        qr_data = f"http://127.0.0.1:8000/attendance/{topic_id}/submit_attendance/?timestamp={timestamp}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # Store the latest timestamp in the session
        request.session['latest_qr_timestamp'] = timestamp
        request.session['attendance_stopped'] = False

        return render(request, 'qr_code.html', {'qr_code': img_str, 'topic': topic, 'timestamp': timestamp})

def download_topic_details_as_csv(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    entries = topic.attendanceentry_set.all()

    response = HttpResponse(content_type='text/csv')
    filename = f"{slugify(topic.title)}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Serial Number', 'Name', 'Roll Number'])

    for index, entry in enumerate(entries, start=1):
        writer.writerow([index, entry.name, entry.roll_number])

    return response
class HomeView(APIView):
    def get(self, request):
        return render(request, 'home.html')

class MyView(View):
    def get(self, request):
        # Generate QR code for a specific text
        qr_code_text = "Your QR Code Text Here"
        qr_code_img = generate_qr_code(qr_code_text)

        # Example logic: Render a template with QR code image
        return render(request, 'my_template.html', {'qr_code_img': qr_code_img})

class DashboardView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        user = request.user
        topics = Topic.objects.filter(user=user)
        topic_count = topics.count()

        # Pagination logic
        page = request.GET.get('page', 1)
        paginator = Paginator(topics, 10)  # Show 10 topics per page

        try:
            topics = paginator.page(page)
        except PageNotAnInteger:
            topics = paginator.page(1)
        except EmptyPage:
            topics = paginator.page(paginator.num_pages)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            topics_html = render_to_string('includes/topics_list.html', {'topics': topics})
            return JsonResponse({'topics_html': topics_html})

        return render(request, 'dashboard.html', {
            'topics': topics,
            'topic_count': topic_count,
            'paginator': paginator
        })

    def post(self, request):
        order = request.POST.getlist('order[]')
        for index, topic_id in enumerate(order):
            topic = Topic.objects.get(id=topic_id, user=request.user)
            topic.order = index
            topic.save()
        return JsonResponse({'status': 'success'})

class UserLoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return render(request, 'login.html')

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'registration.html', {'error_message': None})

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        if not (username and email and password):
            return Response({'detail': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            error_message = 'Username already exists. Please choose a different username.'
            return render(request, 'registration.html', {'error_message': error_message})
        user = User.objects.create_user(username=username, email=email, password=password)
        if user:
            return redirect('login')
        return Response({'detail': 'Registration failed'}, status=status.HTTP_400_BAD_REQUEST)

class CreateTopicView(LoginRequiredMixin, View):
    def get(self, request):
        form = TopicForm()
        return render(request, 'create_topic.html', {'form': form})

    def post(self, request):
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user
            topic.save()
            return redirect('dashboard')
        return render(request, 'create_topic.html', {'form': form})

class TopicDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk, user=request.user)
        query = request.GET.get('query', '')
        if query:
            entries = topic.attendanceentry_set.filter(
                Q(name__icontains=query) | Q(roll_number__icontains=query)
            )
            if request.is_ajax():
                return render(request, 'partials/entries_list.html', {'entries': entries})
        else:
            entries = topic.attendanceentry_set.all()
        return render(request, 'topic_detail.html', {'topic': topic, 'entries': entries})

class TopicUpdateView(UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = 'update_topic.html'
    context_object_name = 'topic'
    success_url = reverse_lazy('dashboard')

class TopicDeleteView(DeleteView):
    model = Topic
    template_name = 'confirm_delete_topic.html'
    context_object_name = 'topic'
    success_url = reverse_lazy('dashboard')


from django.shortcuts import render

class SubmitAttendanceView(View):
    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        timestamp = request.GET.get('timestamp')

        client_ip = get_client_ip(request)
        server_ip = request.META.get('SERVER_ADDR', '127.0.0.1')

        if not is_same_subnet(client_ip, server_ip):
            return render(request, 'wifierror.html')

        if not timestamp or not self.is_qr_code_valid(timestamp, request.session.get('latest_qr_timestamp'), request.session.get('attendance_stopped')):
            return render(request, 'attendance_error.html')

        # Store the necessary information in the session
        request.session['topic_id'] = topic_id
        request.session['timestamp'] = timestamp

        # Render loading page with JavaScript redirect to form
        return render(request, 'loading.html', {'topic_id': topic_id})

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        timestamp = request.session.get('timestamp')

        if not timestamp or not self.is_qr_code_valid(timestamp, request.session.get('latest_qr_timestamp'), request.session.get('attendance_stopped')):
            return render(request, 'attendance_error.html')

        device_identifier = self.get_device_identifier(request)
        if not device_identifier:
            device_identifier = str(uuid.uuid4())  # Generate a unique identifier
            response.set_cookie('device_identifier', device_identifier)
        now = timezone.now()
        last_submission = AttendanceEntry.objects.filter(device_identifier=device_identifier).order_by('-submission_time').first()

        if last_submission and now - last_submission.submission_time < timedelta(minutes=50):
            # Redirect to a message page saying user needs to wait
            return render(request, 'wait_page.html', {'minutes_left': 50 - (now - last_submission.submission_time).seconds // 60})

        form = AttendanceEntryForm(request.POST, request.FILES)
        if form.is_valid():
            attendance_entry = form.save(commit=False)
            attendance_entry.topic = topic
            attendance_entry.save()
            return render(request, 'attendance_success.html')
        return render(request, 'attendance_form.html', {'form': form, 'topic': topic})

    def get_device_identifier(self, request):
        # This function generates a unique identifier for the device
        return request.META.get('REMOTE_ADDR', '')

    def is_qr_code_valid(self, timestamp, latest_timestamp, attendance_stopped):
        if attendance_stopped:
            return False

        if not latest_timestamp:
            return False

        try:
            qr_code_time = datetime.fromtimestamp(int(timestamp), timezone.utc)
            latest_qr_code_time = datetime.fromtimestamp(int(latest_timestamp), timezone.utc)
            if qr_code_time != latest_qr_code_time:
                return False
            if timezone.now() - qr_code_time > timedelta(minutes=2):
                return False
            return True
        except ValueError:
            return False

class StopAttendanceView(View):
    def post(self, request, topic_id):
        request.session['attendance_stopped'] = True
        return redirect('topic_detail', pk=topic_id)

def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def qr_code_view(request):
    # Use the current time as the data for the QR code to ensure it's unique every 2 minutes
    current_time = time.time()
    data = str(int(current_time) // 120)  # Changes every 2 minutes
    qr_code = generate_qr(data)

    return render(request, 'qr_code.html', {'qr_code': qr_code})

def download_all_topics_and_entries_as_csv(request):
    # Fetch the username of the user
    username = request.user.username

    # Fetch all topics for the logged-in user and their entries
    topics = Topic.objects.filter(user=request.user)

    # Generate CSV content
    csv_content = StringIO()
    writer = csv.writer(csv_content)
    writer.writerow(['Topic', 'Name', 'Roll Number'])
    for topic in topics:
        entries = topic.attendanceentry_set.all()
        for entry in entries:
            writer.writerow([topic.title, entry.name, entry.roll_number])

    # Serve the CSV file for download
    filename = f"{slugify(username)}_all_topics_and_entries.csv"
    response = HttpResponse(csv_content.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

class AddManualEntryView(View):
    def get(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        form = AttendanceEntryForm()
        return render(request, 'attendance_form.html', {'form': form, 'topic': topic})

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        form = AttendanceEntryForm(request.POST)
        if form.is_valid():
            attendance_entry = form.save(commit=False)
            attendance_entry.topic = topic
            attendance_entry.save()
            return redirect('topic_detail', topic_id=topic_id)
        return render(request, 'attendance_form.html', {'form': form, 'topic': topic})

def reorder_topics(request):
    if request.method == 'POST':
        order = request.POST.getlist('order[]')
        for index, topic_id in enumerate(order):
            topic = Topic.objects.get(id=topic_id)
            topic.position = index
            topic.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
