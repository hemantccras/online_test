# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import Question, TestAttempt
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Set the password
            user.save()
            login(request, user)  # Log the user in after registration
            return redirect('dashboard')  # Redirect to the dashboard or wherever
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    attempts = TestAttempt.objects.filter(user=request.user).order_by('-attempt_date')
    return render(request, 'dashboard.html', {
        'attempts': attempts,
        'can_take_test': not attempts.exists() or not attempts.first().passed
    })

# @login_required
# def take_test(request):
#     if request.method == 'POST':
#         questions = Question.objects.all()
#         score = 0
#         for question in questions:
#             answer = request.POST.get(f'question_{question.id}')
#             if answer == question.correct_answer:
#                 score += 1
        
#         passed = score >= 18
#         TestAttempt.objects.create(
#             user=request.user,
#             score=score,
#             passed=passed
#         )
        
#         if passed:
#             messages.success(request, 'Congratulations! You have passed the test.')
#             return redirect('certificate')
#         else:
#             messages.warning(request, f'You scored {score}/20. You need 18 to pass. You can retry the test.')
#         return redirect('dashboard')
    
#     questions = Question.objects.all()
#     return render(request, 'test.html', {'questions': questions})

# @login_required
# def certificate(request):
#     latest_attempt = TestAttempt.objects.filter(user=request.user, passed=True).first()
#     if not latest_attempt:
#         return redirect('dashboard')
#     return render(request, 'certificate.html', {
#         'user': request.user,
#         'date': latest_attempt.attempt_date
#     })


from django.http import HttpResponse
from .utils import generate_certificate, send_certificate_email

@login_required
def take_test(request):
   
    if TestAttempt.objects.filter(user=request.user, passed=True).exists():
        return redirect("dashboard")

    if request.method == 'POST':
        questions = Question.objects.all()
        score = 0
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            if answer == question.correct_answer:
                score += 1
        
        passed = score >= 18
        attempt = TestAttempt.objects.create(
            user=request.user,
            score=score,
            passed=passed
        )
        
        if passed:
            # Generate certificate and send email
            pdf_buffer = generate_certificate(request.user, attempt.attempt_date)
            send_certificate_email(request.user, pdf_buffer)
            
            messages.success(request, 'Congratulations! You have passed the test. Your certificate has been emailed to you.')
            return redirect('certificate')
        else:
            messages.warning(request, f'You scored {score}/25. You need 18 to pass. You can retry the test.')
        return redirect('dashboard')
    
    questions = Question.objects.all()
    return render(request, 'test.html', {'questions': questions})

@login_required
def certificate(request):
    latest_attempt = TestAttempt.objects.filter(user=request.user, passed=True).first()
    if not latest_attempt:
        return redirect('dashboard')
    
    if 'download' in request.GET:
            # Generate JPEG certificate (make sure generate_certificate_image returns a JPEG image buffer)
            image_buffer = generate_certificate(request.user, latest_attempt.attempt_date)

            if image_buffer:
                # Create response with JPEG
                response = HttpResponse(image_buffer.getvalue(), content_type='image/jpeg')
                response['Content-Disposition'] = f'attachment; filename=certificate_{request.user.full_name}.jpg'  # Correct file extension
                return response
            else:
                return HttpResponse("Error generating certificate", status=500)
    
    return render(request, 'certificate.html', {
        'user': request.user,
        'date': latest_attempt.attempt_date
    })