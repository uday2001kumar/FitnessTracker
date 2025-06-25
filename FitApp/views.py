from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
# Create your views here.
def index(request):
    email=request.session.get("email")
    if email:
        return redirect(home)
    return render(request,'home.html')

def signup(request):
    email=request.session.get("email")
    if email:
        redirect(home)
    return render(request,'signup.html')
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile

def signupview(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        fitness_level = request.POST.get('fitness_level')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        photo = request.FILES.get('photo')

        # Basic validations
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if UserProfile.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        try:
            profile = UserProfile.objects.create(
                name=name,
                username=username,
                age=int(age),
                gender=gender,
                date_of_birth=dob,  # Must be YYYY-MM-DD or parsed
                height=float(height),
                weight=float(weight),
                fitness_level=fitness_level,
                email=email,
                photo=photo,
                date_joined=timezone.now(),
                password=password
            )
            profile.save()
            messages.success(request, "Signup successful! Please login.")
            return render(request,'signup.html')  # Use redirect after POST

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('signup')

    return render(request, 'signup.html')

def login(request):
    if request.method=='POST':
        email=request.POST['email']
        pas=request.POST['password']
        if UserProfile.objects.filter(email=email,password=pas).exists():
            request.session["email"]=email
            request.session["pas"]=pas
            return redirect(home)
        return render(request,'login.html',{'msg':"Email or Password are Invalid"})
    email=request.session.get("email")
    if email:
        return redirect(home)
    return render(request,'login.html')

def adminlogin(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        if username=="admin" and password=="admin":
            return redirect('admin_dashboard')
        else:
            messages.error(request,"Invalid Username or Password")
    return render(request,'adminlogin.html')

def about(request):
    return render(request,'about.html')

def home(request):
    email=request.session.get("email")
    if email:
        return render(request,'home2.html',{'email':email})
    return render(request,'home2.html')

def logout(request):
    email=request.session.get("email")
    if email:
        request.session.flush()
        return redirect(index)
    return render(request,'login.html')
# ===================================================================
# Profile
def profile_view(request):
    # Check login via session
    if 'email' not in request.session:
        messages.error(request, "Please log in to view your profile.")
        return redirect('login')

    user_email = request.session['email']
    try:
        userprofile = UserProfile.objects.get(email=user_email)
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('login')

    return render(request, 'profile.html', {'userprofile': userprofile})

def profile(request):
    user_email = request.session.get('email')
    try:
        userprofile = UserProfile.objects.get(email=user_email)
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('login')

    age = userprofile.age
    height_cm = userprofile.height
    weight = userprofile.weight
    gender = userprofile.gender

    height_m = height_cm / 100
    bmi = round(weight / (height_m ** 2), 2)
    bmi_status = "Thin" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
    from datetime import date
    today=date.today()
    if gender.lower() == "male":
        bmr = round(10 * weight + 6.25 * height_cm - 5 * age + 5)
        lbm = round(0.407 * weight + 0.267 * height_cm - 19.2, 2)
    else:
        bmr = round(10 * weight + 6.25 * height_cm - 5 * age - 161)
        lbm = round(0.252 * weight + 0.473 * height_cm - 48.3, 2)

    # Classifying BMR status
    if bmr < 1500:
        bmr_status = "Low"
    elif bmr <= 2500:
        bmr_status = "Normal"
    else:
        bmr_status = "High"

    fat_mass = round(weight - lbm, 2)

    # Fat Percentage
    fat_percentage = round((fat_mass / weight) * 100, 1)
    if fat_percentage < 10:
        fat_status = "Low"
    elif fat_percentage <= 25:
        fat_status = "Standard"
    else:
        fat_status = "High"


    # Approximate total body water (TBW) in % of body weight
    if gender.lower() == "male":
        moisture = round(0.6 * weight, 2)  # 60% of body weight
    else:
        moisture = round(0.5 * weight, 2)  # 50% of body weight

    # Now classify moisture level
    if moisture < 40:
        moisture_status = "Low"
    elif moisture <= 60:
        moisture_status = "Standard"
    else:
        moisture_status = "High"


    # This is a very basic estimation formula, not medically precise.
    vfi = round((bmi + age / 10) - (lbm / weight) * 10, 2)
    if vfi<=10:
        vfi_status="Low"
    elif vfi>10 and vfi<=15:
        vfi_status="Normal"
    else:
        vfi_status="High"

    # Standard Weight Calculation
    if gender.lower() == "male":
        standard_weight = round(50 + 0.91 * (height_cm - 152.4))
    else:
        standard_weight = round(45.5 + 0.91 * (height_cm - 152.4))

    weight_control = round(weight - standard_weight, 2)
    if weight_control > 0:
        control_status = f"Overweight"
    elif weight_control < 0:
        control_status = f"Thin"
    else:
        control_status = "Normal"

    muscle_mass = round(0.5 * lbm, 2)
    bone_mass = round(0.15 * lbm, 2)
    context = {
        'userprofile':userprofile,
        'today':today,
        'weight':weight,
        'control_status':control_status,
        'height':height_cm,


        'bmi': bmi,
        'bmi_status': bmi_status,

        'fat_percentage': fat_percentage,
        'fat_status':fat_status,
        
        'moisture':moisture,
        'moisture_status':moisture_status,


        'bmr': bmr,
        'bmr_status': bmr_status,

        'lean_body_mass': lbm,
        
        'vfi':vfi,
        'vfi_status':vfi_status,

        'fat_mass':fat_mass,
        'standard_weight':standard_weight,
        'weight_control':weight_control,
        'muscle_mass':muscle_mass,
        'bone_mass':bone_mass
        
    }

    return render(request, 'profile/sug.html', context)
from django.core.mail import send_mail
from django.conf import settings
def forget_Password(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        try:
            user = UserProfile.objects.get(email=email)
            password = user.password  # ⚠️ Assumes password is stored as plaintext (NOT RECOMMENDED)

            subject = "Welcome to FitnessTracker App!"
            message = f"Your Password is: {password}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, "Password sent to your email!")
        except UserProfile.DoesNotExist:
            messages.error(request, "Email not registered!")
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")
    
    return render(request, 'forget.html')


def update_profile(request):
    if request.method=="POST":
        user_email=request.session['email']
        name=request.POST["name"]
        age=int(request.POST["age"])
        gender=request.POST["gender"]
        dob=request.POST["dob"]
        height=float(request.POST["height"])
        weight=float(request.POST["weight"])
        fitness_level=request.POST["fitness_level"]
        email=request.POST["email"]
        user=UserProfile.objects.get(email=user_email)
        user.name=name
        user.age=age
        user.gender=gender
        user.date_joined=dob
        user.height=height
        user.weight=weight
        user.fitness_level=fitness_level
        user.email=email
        user.save()
        return redirect('profile')  
    user_email = request.session['email']
    if user_email:
        user_details=UserProfile.objects.get(email=user_email)
        return render(request,'profile/update.html',{'userprofile':user_details})
    
# ===============================================================================
# ===============================================================================
# ===============================================================================
# Workout
from .models import Add_Workout
from datetime import datetime

from django.db.models import Sum
from datetime import date

from datetime import date
from django.db.models import Sum

def workouthome(request):
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    today = date.today()

    # Total number of workouts
    total_workouts = Admin_Workout.objects.count()

    # Completed workouts today
    completed_today = Add_Workout.objects.filter(user=user, workout_date__date=today).count()

    # Calories burned today
    calories_burned_today = Add_Workout.objects.filter(user=user, workout_date__date=today).aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0

    # Total time today (in minutes)
    total_minutes = Add_Workout.objects.filter(user=user, workout_date__date=today).aggregate(Sum('workout_duration'))['workout_duration__sum'] or 0

    # Average calories burned per workout today
    avg_calories = calories_burned_today // completed_today if completed_today else 0

    # Workout type today (optional)
    logs_today = Add_Workout.objects.filter(user=user, workout_date__date=today)
    workout_type_today = logs_today.first().workout_type if logs_today.exists() else "N/A"
    return render(request, 'workout/work_home.html', {
        'total_workouts': total_workouts,
        'completed_today': completed_today,
        'calories_burned_today': calories_burned_today,
        'today': today,
        'total_time_today': f"{total_minutes // 60}h {total_minutes % 60}m",
        'avg_calories': avg_calories,
        'workout_type_today': workout_type_today,
        'user':user
    })


def workout(request):
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    return render(request,'workout/workout.html',{'user':user})

def weight_loss(request):
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    workout_loss=Admin_Workout.objects.filter(category="loss")
    return render(request,'workout/weight_loss.html',{'workout_loss':workout_loss,'user':user})

def weight_gain(request):
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    workout_gain=Admin_Workout.objects.filter(category="gain")
    return render(request,'workout/weight_gain.html',{'workout_gain':workout_gain,'user':user})

from datetime import datetime
from django.shortcuts import render
from django.contrib import messages
from .models import Add_Workout, UserProfile

def calculate_calories_burned(met, weight_kg, duration_minutes):
    duration_hours = duration_minutes / 60
    return round(met * weight_kg * duration_hours, 2)

def add_workout(request):
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    weight_loss_workouts = Admin_Workout.objects.filter(category='loss')
    weight_gain_workouts = Admin_Workout.objects.filter(category='gain')
    for i in weight_loss_workouts:
        print(i)
    context = {
        'weight_loss_workouts': weight_loss_workouts,
        'weight_gain_workouts': weight_gain_workouts,
        'user':user
    }
    if request.method == "POST":
        workout_type = request.POST["workout_type"]
        workout_name = request.POST["workout_name"]
        duration = int(request.POST["duration"])
        work_date = request.POST["date"]
        selected_date = datetime.strptime(work_date, "%Y-%m-%d").date()
        current_time = datetime.now().time()
        combined_datetime = datetime.combine(selected_date, current_time)

        email = request.session.get('email')
        if email:
            user = UserProfile.objects.get(email=email)
            admin=Admin_Workout.objects.get(workout_name=workout_name)
            met_value=admin.met_value
            # Fetch user weight and height
            weight = user.weight  # Ensure weight field exists in your UserProfile model

            # Calculate calories burned
            calories_burned = calculate_calories_burned(met_value, weight, duration)

            # Save the workout with calories burned
            m2 = Add_Workout(
                user=user,
                workout_type=workout_type,
                workout_name=workout_name,
                workout_duration=duration,
                workout_date=combined_datetime,
                calories_burned=calories_burned 
            )
            m2.save()

            messages.success(request, f"Calories burned: {calories_burned} kcal")
            return render(request, 'workout/add_workout.html',context)

        else:
            print("Session expired or user not logged in")

    return render(request, 'workout/add_workout.html',context)

from django.utils import timezone
from datetime import datetime

def view_past_workouts(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    try:
        user = UserProfile.objects.get(email=email)
        # Get date from query param (GET request)
        search_date = request.GET.get('date')

        if search_date:
            try:
                # Parse user input to date
                search_date_obj = datetime.strptime(search_date, "%Y-%m-%d").date()
                workouts = Add_Workout.objects.filter(
                    user=user,
                    workout_date__date=search_date_obj
                ).order_by('-workout_date')
            except ValueError:
                messages.error(request, "Invalid date format.")
                workouts = []
        else:
            # Default: filter today's workouts
            today = timezone.now().date()
            workouts = Add_Workout.objects.filter(
                user=user,
                workout_date__date=today
            ).order_by('-workout_date')

        return render(request, 'workout/view_past_workouts.html', {'data': workouts,'user':user})

    except UserProfile.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')


def delete_workout(request,pk):
    
    m4=Add_Workout.objects.get(id=pk)
    m4.delete()
    messages.success(request,"Workout Deleted Successfully!")
    return redirect(view_past_workouts)


from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile, Add_Workout

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
def generate_weekly_report(request):
    email = request.session.get('email')
    if not email:
        return None

    user = UserProfile.objects.filter(email=email).first()
    if not user:
        return None

    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    workouts = (
        Add_Workout.objects
        .filter(user=user, workout_date__date__range=(seven_days_ago, today))
        .values('workout_date__date')
        .annotate(total_calories=Sum('calories_burned'))
        .order_by('workout_date__date')
    )

    # Prepare a dict with all 7 days initialized to 0
    date_calories = { (today - timedelta(days=i)): 0 for i in range(6, -1, -1) }

    for workout in workouts:
        date = workout['workout_date__date']
        total = workout['total_calories']
        date_calories[date] = total

    return date_calories
def generate_chart(request):
    date_calories = generate_weekly_report(request)

    if not date_calories:
        return None

    dates = list(date_calories.keys())
    calories = list(date_calories.values())

    # Format x-axis labels as weekday names (e.g., Apr 12)
    labels = [date.strftime('%b %d') for date in dates]

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    fig, ax = plt.subplots(figsize=(8, 5))

    # 📈 Use plot() instead of bar()
    ax.plot(labels, calories, color='orange', marker='o', linewidth=2, linestyle='-')
    
    # 🎯 Add titles and labels
    ax.set_title("Calories Burned Over Last 7 Days", fontsize=14)
    ax.set_ylabel("Calories Burned", fontsize=12)
    ax.set_xlabel("Day", fontsize=12)

    # 📊 Optional: Enhance appearance
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')

    # ⏳ Save image to base64
    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    return img_base64
def show_weekly_chart(request):
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    chart_data = generate_chart(request)
    if not chart_data:
        return redirect('login')
    return render(request, 'workout/chart1.html', {'chart_data': chart_data,'user':user})

def suggession(request):
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    return render(request,'workout/suggesions.html',{'user':user})
# -----------------------------------------------------
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

from django.shortcuts import render, redirect
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from .models import UserProfile, Add_Workout
from calendar import monthrange

from datetime import datetime, timedelta
from django.utils import timezone
from calendar import monthrange
from django.db.models import Sum
from datetime import datetime, timedelta
from calendar import monthrange
from django.utils import timezone
from django.db.models import Sum, DateField
from django.db.models.functions import Cast

def generate_monthly_report(request):
    # Get user email from session
    email = request.session.get('email')
    if not email:
        return None, None

    # Get the user object from email
    user = UserProfile.objects.filter(email=email).first()
    if not user:
        return None, None

    # Get the selected month from the form (e.g., "2025-05")
    selected_month = request.GET.get('month', None)
    if not selected_month:
        return None, None

    # Parse the selected month to get the start and end dates
    year, month = map(int, selected_month.split('-'))
    first_day_of_month = timezone.make_aware(datetime(year, month, 1))
    last_day_of_month = timezone.make_aware(datetime(year, month, monthrange(year, month)[1]))

    # Query and annotate workouts
    workouts = (
        Add_Workout.objects
        .filter(user=user, workout_date__date__range=(first_day_of_month.date(), last_day_of_month.date()))
        .annotate(date=Cast('workout_date', DateField()))
        .values('date', 'workout_date','workout_name')
        .annotate(total_calories=Sum('calories_burned'))
        .order_by('date')
    )

    # Initialize a dict for each day of the month with 0 calories
    date_calories = {
        (first_day_of_month.date() + timedelta(days=i)): 0
        for i in range((last_day_of_month.date() - first_day_of_month.date()).days + 1)
    }
    workout_details = []

    # Fill in the calories from the query
    for workout in workouts:
        date = workout['date']  # ✅ use the casted 'date'
        total = workout['total_calories']
        date_calories[date] = total
        workout_details.append(workout)

    return date_calories, workout_details




def generate_monthly_chart(request):
    date_calories, _ = generate_monthly_report(request)

    if not date_calories:
        return None

    dates = list(date_calories.keys())
    calories = list(date_calories.values())

    # Format x-axis labels as day numbers (e.g., 12)
    labels = [date.strftime('%d') for date in dates]

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    fig, ax = plt.subplots(figsize=(10, 5))

    # 📈 Use plot() for a line chart
    ax.plot(labels, calories, color='green', marker='o', linewidth=2, linestyle='-')

    # 🎯 Add titles and labels
    ax.set_title("Calories Burned Over Selected Month", fontsize=14)
    ax.set_ylabel("Calories Burned", fontsize=12)
    ax.set_xlabel("Day", fontsize=12)

    # 📊 Optional: Enhance appearance
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')

    # ⏳ Save image to base64
    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    return img_base64
def monthly_report_workouts(request):
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    selected_month = request.GET.get('month')
    selected_month_display = None
    selected_month_value = None  # NEW

    if selected_month:
        date_calories, workout_details = generate_monthly_report(request)
        chart_data = generate_monthly_chart(request)
        try:
            dt = datetime.strptime(selected_month, "%Y-%m")
            selected_month_display = dt.strftime("%B %Y")
            selected_month_value = selected_month  # Already in YYYY-MM
        except ValueError:
            selected_month_display = "Invalid"
            selected_month_value = ""
    else:
        date_calories = {}
        workout_details = []
        chart_data = None
        selected_month_display = "No month selected"
        selected_month_value = date.today().strftime("%Y-%m")  # Default to current month

    return render(request, 'workout/monthly_report.html', {
        'chart_data': chart_data,
        'workout_details': workout_details,
        'selected_month_display': selected_month_display,
        'selected_month_value': selected_month_value,  # NEW
        'date_calories': date_calories,
        'today': date.today(),
        'user':user
    })

from datetime import datetime
from django.shortcuts import render
from .models import Add_Workout  # Ensure you have the correct model imported

from datetime import datetime
from django.db.models import Sum
from django.shortcuts import render
from .models import Add_Workout

def compare(request):
    # Initialize all variables
    data = None
    compare_data = None
    data_total_calories = 0
    com_data_total_calories = 0
    data_total_duration = 0
    com_data_total_duration = 0

    if request.method == 'POST':
        date = request.POST.get('date')  # Get the date selected by the user
        compare_date = request.POST.get('compare_date')  # Get the comparison date selected by the user

        # Get data for the selected date
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                data = Add_Workout.objects.filter(workout_date__date=date_obj)
                data_total_calories = data.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
                data_total_duration = data.aggregate(Sum('workout_duration'))['workout_duration__sum'] or 0
            except ValueError:
                data = Add_Workout.objects.none()

        # Get data for the comparison date
        if compare_date:
            try:
                compare_date_obj = datetime.strptime(compare_date, '%Y-%m-%d').date()
                compare_data = Add_Workout.objects.filter(workout_date__date=compare_date_obj)
                com_data_total_calories = compare_data.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0
                com_data_total_duration = compare_data.aggregate(Sum('workout_duration'))['workout_duration__sum'] or 0
            except ValueError:
                compare_data = Add_Workout.objects.none()

    # Safely calculate even if it's a GET request
    calories_difference = data_total_calories - com_data_total_calories
    email = request.session.get("email")
    if email:
        user = UserProfile.objects.get(email=email)
    return render(request, 'workout/compare.html', {
        'data': data,
        'data_total_calories': data_total_calories,
        'compare_data': compare_data,
        'com_data_total_calories': com_data_total_calories,
        'calories_difference': calories_difference,
        'data_total_duration': data_total_duration,
        'com_data_total_duration': com_data_total_duration,
        'user':user
    })



# ===================================================

# ==========================================================
# Nutrition
from django.shortcuts import render
from datetime import date
from .models import Admin_Nutrition  # Adjust the model import according to your project structure

from datetime import date
from django.db.models import Sum
from django.db.models.functions import TruncDate
from datetime import date, timedelta
from django.db.models import Sum
from django.db.models.functions import TruncDate
import matplotlib.pyplot as plt
import io
import base64
from django.utils import timezone

def nutrition_home(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Please log in again.")
        return redirect('login')

    user = UserProfile.objects.get(email=email)
    today = timezone.now().date()  # Use timezone-aware date
    today_nutrition = Add_Nutrition.objects.annotate(date_only=TruncDate('date_added')).filter(user=user, date_only=today)
    
    # Aggregating nutrition data for today
    total_nutritions = Admin_Nutrition.objects.count()
    consumed_today = today_nutrition.count()
    calories_agg = today_nutrition.aggregate(total=Sum('total_calories'))
    calories_consumed_today = calories_agg['total'] or 0
    total_meals_today = today_nutrition.values('goal_type').distinct().count()
    nutrition_type_today = today_nutrition.values('goal_type').first()
    avg_calories = calories_consumed_today / total_meals_today if total_meals_today > 0 else 0
    
   
    context = {
        'total_nutritions': total_nutritions,
        'consumed_today': consumed_today,
        'calories_consumed_today': calories_consumed_today,
        'total_meals_today': total_meals_today,
        'nutrition_type_today': nutrition_type_today['goal_type'] if nutrition_type_today else 'N/A',
        'avg_calories': avg_calories,
        'today': today,
        'user':user
    }

    return render(request, 'nutrition/nutrition_home.html', context)



def nutritions(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Please log in again.")
        return redirect('login')
    else:
        user=UserProfile.objects.get(email=email)

    return render(request,'nutrition/nutritions.html',{'user':user})
from .models import Add_Nutrition
def add_nutrition(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Please log in again.")
        return redirect('login')
    else:
        user=UserProfile.objects.get(email=email)

    weight_loss_nutritions = Admin_Nutrition.objects.filter(goal_type='Weight Loss')
    weight_gain_nutritions = Admin_Nutrition.objects.filter(goal_type='Weight Gain')

    context = {
        'weight_loss_nutritions': weight_loss_nutritions,
        'weight_gain_nutritions': weight_gain_nutritions,
        'user':user
    }

    if request.method == "POST":
        food_item_name = request.POST.get('food_item')
        servings = float(request.POST.get('servings'))
        date_added = request.POST.get('date_added')
        goal_type = request.POST.get('goal_type')
        email = request.session.get('email')

        if not email:
            messages.error(request, "Session expired. Please log in again.")
            return redirect('login')

        selected_date = datetime.strptime(date_added, "%Y-%m-%d").date()
        current_time = datetime.now().time()
        combined_datetime = datetime.combine(selected_date, current_time)

        user = UserProfile.objects.get(email=email)
        food_data = Admin_Nutrition.objects.get(name=food_item_name)

        # ✅ Calculate total calories
        calories_per_serving = food_data.calories_per_serving
        total_calories = servings * calories_per_serving

        # ✅ Save nutrition entry
        m5 = Add_Nutrition(
            user=user,
            food_item=food_item_name,
            servings=servings,
            date_added=combined_datetime,
            goal_type=goal_type,
            total_calories=total_calories,
        )
        m5.save()

        messages.success(request, f"Nutrition Added Successfully! Total Calories: {total_calories:.2f} kcal ✅")
        return render(request, 'nutrition/add_nutrition.html', context)
    return render(request, 'nutrition/add_nutrition.html', context)
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile, Add_Nutrition

from datetime import datetime, date
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile, Add_Nutrition

def view_nutrition(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    try:
        user = UserProfile.objects.get(email=email)

        today = date.today()
        search_date_str = request.GET.get('search_date')

        if search_date_str:
            try:
                search_date = datetime.strptime(search_date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                search_date = today
        else:
            search_date = today

        # Filter records for the selected date
        m6 = Add_Nutrition.objects.filter(
            user=user, date_added__date=search_date
        ).order_by('-date_added')

        return render(request, 'nutrition/view_nutrition.html', {
            'data': m6,
            'search_date': search_date.strftime("%Y-%m-%d") ,
             'user':user 
        })

    except UserProfile.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')


import io  
def weekly_progress_chart(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, "Please log in again.")
        return redirect('login')

    user = UserProfile.objects.get(email=email)
    today = timezone.now().date()
    start_date = today - timedelta(days=6)

    # Prepare data for the last 7 days
    dates = [start_date + timedelta(days=i) for i in range(7)]
    calories_data = []

    for date in dates:
        total = Add_Nutrition.objects.filter(user=user, date_added__date=date).aggregate(total=Sum('total_calories'))['total'] or 0
        calories_data.append(total)
    date_labels = [date.strftime('%b %d') for date in dates]
    # Plot using matplotlib
    plt.figure(figsize=(8, 4))
    plt.plot(date_labels, calories_data, marker='o', linestyle='-', color='green')
    plt.title('Weekly Calorie Progress')
    plt.xlabel('Date')
    plt.ylabel('Total Calories')
    plt.grid(True)
    plt.tight_layout()

    # Save image to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graph = base64.b64encode(image_png).decode('utf-8')
    plt.close()

    return render(request, 'nutrition/weekly_progress.html', {'graph': graph,'user':user})

from dateutil.relativedelta import relativedelta
def monthly_report_nutrition(request):
    email = request.session.get("email")
    if not email:
        return render(request, 'nutrition/monthly_report.html', {'graph': None})

    user = UserProfile.objects.get(email=email)

    # Handle selected month (from input)
    selected_month = request.GET.get('month')
    
    if selected_month:
        # Parse year and month from the input (format: YYYY-MM)
        year, month = map(int, selected_month.split('-'))
        start_date = datetime(year, month, 1).date()
    else:
        # Default to current month
        today = timezone.now().date()
        start_date = today.replace(day=1)
        selected_month = start_date.strftime('%Y-%m')  # for re-filling form

    end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)

    # Generate all dates of the month
    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    calories_data = []

    for date in dates:
        total = Add_Nutrition.objects.filter(user=user, date_added__date=date).aggregate(total=Sum('total_calories'))['total'] or 0
        calories_data.append(total)

    date_labels = [date.strftime('%d') for date in dates]

    # Plot the graph
    plt.figure(figsize=(10, 5))
    plt.plot(date_labels, calories_data, marker='o', linestyle='-', color='#007bff')
    plt.title(f'Calorie Progress for {start_date.strftime("%B %Y")}')
    plt.xlabel('Date')
    plt.ylabel('Total Calories')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png).decode('utf-8')
    plt.close()
    month_records = Add_Nutrition.objects.filter(
        user=user,
        date_added__date__range=(start_date, end_date)
    ).order_by('date_added')
    return render(request, 'nutrition/monthly_report.html', {
        'graph': graph,
        'selected_month': selected_month,
        'month_records': month_records,
        'user':user
    })

def delete_nutrition(request,pk):
    m7=Add_Nutrition.objects.get(id=pk)
    m7.delete()
    messages.success(request,"Nutrition Deleted Successfully!")
    return redirect(view_nutrition)

def food_weight_loss(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Please log in again.")
        return redirect('login')
    else:
        user=UserProfile.objects.get(email=email)
    food_weight_loss=Admin_Nutrition.objects.filter(goal_type="Weight Loss")
    context = {
        'food_weight_loss': food_weight_loss,
        'user':user
    }
    return render(request,'nutrition/food_weight_loss.html',context)

def food_weight_gain(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Please log in again.")
        return redirect('login')
    else:
        user=UserProfile.objects.get(email=email)
    food_weight_gain=Admin_Nutrition.objects.filter(goal_type="Weight Gain")
    context = {
        'food_weight_gain': food_weight_gain,
        'user':user
    }
    return render(request,'nutrition/food_weight_gain.html',context)

def suggesionsn(request):
    email = request.session.get("email")
    if not email:
        messages.error(request, "Please log in again.")
        return redirect('login')
    else:
        user=UserProfile.objects.get(email=email)
    return render(request,'nutrition/suggesions.html',{'user':user})


from django.shortcuts import render
from django.db.models import Sum
from .models import Add_Nutrition, UserProfile

def nutrition_comparison(request):
    data = None
    compare_data = None
    data_total_calories = 0
    com_data_total_calories = 0
    calories_difference = None

    # Get the user's email from session
    email = request.session.get("email")
    
    # If email exists in the session, fetch the user
    if email:
        user = UserProfile.objects.filter(email=email).first()
        if user:
            if request.method == "POST":
                # Get the dates directly from the POST data
                data = request.POST.get('date')
                compare_data = request.POST.get('compare_date')
                
                print(data,compare_data)
                if data and compare_data:
                    # Get nutrition data for the selected date using consumed_date
                    data = Add_Nutrition.objects.filter(user=user, date_added__date=data)
                    data_total_calories = data.aggregate(Sum('total_calories'))['total_calories__sum'] or 0

                    # Get nutrition data for the compare date using consumed_date
                    compare_data = Add_Nutrition.objects.filter(user=user, date_added__date=compare_data)
                    com_data_total_calories = compare_data.aggregate(Sum('total_calories'))['total_calories__sum'] or 0

                    # Calculate the difference in calories consumed
                    calories_difference = data_total_calories-com_data_total_calories

    return render(request, 'nutrition/compare.html', {
        'data': data,
        'compare_data': compare_data,
        'data_total_calories': data_total_calories,
        'com_data_total_calories': com_data_total_calories,
        'calories_difference': calories_difference,
        'user':user
    })


"""=========================================================
   =========================================================
   Admin Panel of the Application
   =========================================================
   =========================================================
   ========================================================="""
# Admin Details
from .models import Admin_Workout,Admin_Nutrition
def admin_dashboard(request):
    user_count=UserProfile.objects.count()
    workout_logged=Admin_Workout.objects.count()
    nutritions=Admin_Nutrition.objects.count()
    return render(request,'admin/admin_dashboard.html',{'user_count':user_count,'workout_logged':workout_logged,'nutritions':nutritions})

def admin_users(request):
    users=UserProfile.objects.all()
    return render(request,'admin/admin_users.html',{'users':users})

def admin_delete_user(request,pk):
    user=UserProfile.objects.get(id=pk)
    user.delete()
    messages.success(request,"User Deleted Successfully!")
    return redirect(admin_users)

def Admin_add_workout(request):
    if request.method=="POST":
        workout_name=request.POST.get('workout_name')
        image=request.FILES.get('image')
        description=request.POST.get('description')
        category=request.POST.get('category')
        met = request.POST.get('met_value')
        if Admin_Workout.objects.filter(workout_name=workout_name).exists():
            messages.error(request,"Workout Already Exist!")
        else:
            workout=Admin_Workout(
                workout_name=workout_name,
                image=image,
                description=description,
                category=category,
                met_value=met
            )
            workout.save()
            messages.success(request,"Workout Add Successful!")
            return redirect(Admin_add_workout)
    return render(request,'admin/add_workouts.html')

def Admin_View_Workouts(request):
    workout=Admin_Workout.objects.all()
    return render(request,'admin/admin_view_workouts.html',{'workouts':workout})
def Admin_Delete_Workout(request):
    workouts=Admin_Workout.objects.all()
    return render(request,'admin/delete_workout.html',{'workouts':workouts})

def Admin_Delete_Workout_List(request,pk):
    d=Admin_Workout.objects.get(id=pk)
    d.delete()
    messages.success(request,"Workout Deleted Successful!")
    return redirect(Admin_Delete_Workout)


def admin_view_user(request,pk):
    user_view=UserProfile.objects.get(id=pk)
    return render(request,'admin/view_user.html',{'user_view':user_view})
def admin_add_nutrition(request):
    if request.method == "POST":
        # Retrieve form data
        name = request.POST.get('food_name')
        description = request.POST.get('description')
        nutrition_type = request.POST.get('goal_type')
        goal_type = request.POST.get('goal_type')
        calories_per_serving = request.POST.get('calories_per_serving')
        protein = request.POST.get('protein')
        carbs = request.POST.get('carbs')
        fats = request.POST.get('fats')
        image = request.FILES.get('image')

        # Check if nutrition already exists
        if Admin_Nutrition.objects.filter(name=name).exists():
            messages.error(request, "Nutrition Item Already Exists!")
        else:
            # Create and save the new nutrition item
            nutrition = Admin_Nutrition(
                name=name,
                description=description,
                nutrition_type=nutrition_type,
                goal_type=goal_type,
                calories_per_serving=calories_per_serving,
                protein=protein,
                carbs=carbs,
                fats=fats,
                image=image
            )
            nutrition.save()
            messages.success(request, "Nutrition Item Added Successfully!")
            return redirect('admin_add_nutrition')  # Redirect after successful form submission

    return render(request, 'admin/add_nutrition.html')
def Admin_View_Nutrition(request):
    nutrition=Admin_Nutrition.objects.all()
    return render(request,'admin/admin_view_nutrition.html',{'nutrition':nutrition})

def Admin_Delete_Nutrition_List(request):
    nutritions = Admin_Nutrition.objects.all()
    return render(request, 'admin/delete_nutrition.html', {'nutritions': nutritions})

def Admin_Delete_Nutrition(request,pk):
    nutrition = Admin_Nutrition.objects.get(id=pk)
    nutrition.delete()
    messages.success(request, "Nutrition item deleted successfully.")
    return redirect('Admin_Delete_Nutrition_List')
    
    