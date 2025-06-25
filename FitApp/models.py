from django.db import models
from django.utils import timezone 

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    height = models.FloatField(help_text="Enter height in centimeters")
    weight = models.FloatField(help_text="Enter weight in kilograms")
    fitness_level = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Other')
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    password=models.CharField(max_length=10)
    def __str__(self):
        return self.name

class Add_Workout(models.Model):
    user=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    WORKOUT_TYPES = [
    ('Weight Loss', 'Weight Loss'),
    ('Weight Gain', 'Weight Gain'),
    ]
    workout_type=models.CharField(max_length=100,choices=WORKOUT_TYPES)
    workout_name=models.CharField(max_length=100,primary_key=True)
    workout_duration=models.IntegerField()
    workout_date=models.DateTimeField(default=timezone.now)
    calories_burned = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.user.username

from django.db import models
from django.utils import timezone

class Add_Nutrition(models.Model):
    GOAL_CHOICES = [
        ('Weight Loss', 'Weight Loss'),
        ('Weight Gain', 'Weight Gain'),
        ('General Fitness', 'General Fitness'),
    ]
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    food_item = models.CharField(max_length=100)
    servings = models.FloatField(default=1.0, help_text="Number of servings")
    date_added = models.DateTimeField(default=timezone.now)
    goal_type = models.CharField(max_length=50, choices=GOAL_CHOICES, default='General Fitness')
    total_calories = models.FloatField(default=0.0)


    def __str__(self):
        return f"{self.user.username} - {self.food_item} ({self.goal_type})"

    
# Admin
class Admin_Workout(models.Model):
    CATEGORY_CHOICES = (
        ('Weight Loss', ' Loss'),
        ('Weight Gain', 'Weight Gain'),
    )

    workout_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='workout_images/')
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    met_value = models.FloatField(default=4.0) 

    def __str__(self):
        return f"{self.workout_name} ({self.get_category_display()})"
    
from django.db import models

class Admin_Nutrition(models.Model):
    NUTRITION_TYPE_CHOICES = [
        ('Protein', 'Protein'),
        ('Carbohydrate', 'Carbohydrate'),
        ('Fat', 'Fat'),
        ('Fiber', 'Fiber'),
        ('Vitamin', 'Vitamin'),
        ('Mineral', 'Mineral'),
        ('Mixed', 'Mixed'),  # For whole foods
    ]

    GOAL_CHOICES = [
        ('Weight Loss', 'Weight Loss'),
        ('Weight Gain', 'Weight Gain')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    nutrition_type = models.CharField(max_length=20, choices=NUTRITION_TYPE_CHOICES)
    calories_per_serving = models.FloatField(help_text="Calories per serving")
    protein = models.FloatField(default=0.0, help_text="Protein (g)")
    carbs = models.FloatField(default=0.0, help_text="Carbohydrates (g)")
    fats = models.FloatField(default=0.0, help_text="Fats (g)")
    goal_type = models.CharField(max_length=50, choices=GOAL_CHOICES)
    image = models.ImageField(upload_to='nutrition_images/', blank=True, null=True)

    def __str__(self):
        return self.name
