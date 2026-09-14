from django.db import models
from users.models import User
from scripts.get_iin import calculate_age
# Create your models here.

class TestTypes(models.Model):
    name = models.CharField(max_length=128, unique=True)
    code_name = models.CharField(max_length=128, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

class TestResults(models.Model):
    iin = models.ForeignKey(User, on_delete=models.CASCADE)
    test_type = models.ForeignKey(TestTypes, on_delete=models.CASCADE)
    date_taken = models.DateTimeField(auto_now_add=True)
    age = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.age and self.iin.b_day:
            self.age = str(calculate_age(str(self.iin.b_day)))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.iin.iin} - {self.test_type.name}"
    
class EyeDescription(models.Model):
    name = models.TextField()

    def __str__(self):
        return f"{self.name}"

class TestImage(models.Model):
    image = models.ImageField(upload_to="test_images/", null=True, blank=True)
    number = models.IntegerField(default='1')

    def __str__(self):
        return f"{self.image}"

class EyeResults(models.Model):
    result_id = models.ForeignKey(TestResults, on_delete=models.CASCADE)
    description = models.ForeignKey(EyeDescription, on_delete=models.CASCADE, related_name='eye_tracking')
    coords = models.JSONField(null=True, blank=True)
    result_image = models.ImageField(upload_to="result_images/", null=True, blank=True)

    def __str__(self):
        return f"{self.result_id} - {self.description}"

class EyeCount(models.Model):
    neitral = models.CharField(max_length=6, null=True, blank=True)
    social = models.CharField(max_length=6, null=True, blank=True)
    image = models.ForeignKey(TestImage, on_delete=models.CASCADE)
    test_result = models.ForeignKey(TestResults, on_delete=models.CASCADE,default=1)

    def __str__(self):
        return f"Image: {self.image} | Neitral: {self.neitral} | Social: {self.social}"

class MChatRiskLevel(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class MChatQuestions(models.Model):
    name = models.TextField()
    number = models.IntegerField(default='1')
    def __str__(self):
        return self.name    
    
class MChat(models.Model):
    result_id = models.ForeignKey(TestResults, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField(null=True, blank=True,default=20)
    risk_level = models.ForeignKey(MChatRiskLevel, on_delete=models.CASCADE, related_name='m_chat')
    question = models.ForeignKey(MChatQuestions, on_delete=models.CASCADE, related_name='m_chat')
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"MChat - {self.result_id} - {self.score} - {self.risk_level}"

class SCQDescriptions(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class SCQQuestions(models.Model):
    name = models.TextField()
    number = models.IntegerField()
    def __str__(self):
        return self.name    
    
class SCQ(models.Model):
    result_id = models.ForeignKey(TestResults, on_delete=models.CASCADE)
    score = models.FloatField(max_length=5)
    total = models.FloatField(max_length=5, null=True, blank=True,default=40)
    description = models.ForeignKey(SCQDescriptions, on_delete=models.CASCADE, related_name='scq')
    question = models.ForeignKey(SCQQuestions, on_delete=models.CASCADE, related_name='scq')
    answer = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"SCQ - {self.result_id} - {self.score} - {self.description}"
    
class CarsDescriptions(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.name}"

class CarsAnswers(models.Model):
    name = models.TextField()
    number = models.IntegerField(default=0)
    score = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.name}"    

class CarsQuestions(models.Model):
    name = models.TextField(null=True, blank=True)
    number = models.IntegerField(default='0')
    answer = models.ForeignKey(CarsAnswers, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name}"    
    
class Cars(models.Model):
    result_id = models.ForeignKey(TestResults, on_delete=models.CASCADE)
    score = models.FloatField(max_length=5)
    total = models.FloatField(max_length=5,default=60)
    description = models.ForeignKey(CarsDescriptions, on_delete=models.CASCADE, related_name='cars')
    question = models.ForeignKey(CarsQuestions, on_delete=models.CASCADE, related_name='cars')
    answer = models.ForeignKey(CarsAnswers, on_delete=models.CASCADE, null=True, blank=True, related_name='cars')

    def __str__(self):
        return f"CARS - {self.result_id} - {self.score} - {self.description}"   

class AtecDescriptions(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.name}"

class AtecQuestionsType(models.Model):
    name = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.name}"   

class AtecAnswers(models.Model):
    name = models.TextField()
    question_type = models.ForeignKey(AtecQuestionsType, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.name}"

class AtecQuestions(models.Model):
    name = models.TextField(null=True, blank=True)
    number = models.IntegerField(default='0')
    type = models.ForeignKey(AtecQuestionsType, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name}"    
    
class Atec(models.Model):
    result_id = models.ForeignKey(TestResults, on_delete=models.CASCADE)
    score = models.FloatField(max_length=5)
    total = models.FloatField(max_length=5,default=77)
    description = models.ForeignKey(AtecDescriptions, on_delete=models.CASCADE, related_name='atec')
    question = models.ForeignKey(AtecQuestions, on_delete=models.CASCADE, related_name='atec')
    answer = models.ForeignKey(AtecAnswers, on_delete=models.CASCADE, null=True, blank=True, related_name='atec')

    def __str__(self):
        return f"ATEC - {self.result_id} - {self.score} - {self.description}"

class CasdDescriptions(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.name}"

class CasdQuestions(models.Model):
    name = models.TextField(null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return f"{self.number}) - {self.name}"    

class CasdAnswers(models.Model):
    name = models.TextField()
    question_type = models.ForeignKey(CasdQuestions, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.name}"

class Casd(models.Model):
    result_id = models.ForeignKey(TestResults, on_delete=models.CASCADE)
    score = models.FloatField(max_length=5)
    total = models.FloatField(max_length=5,default=30)
    description = models.ForeignKey(CasdDescriptions, on_delete=models.CASCADE, related_name='casd')
    question = models.ForeignKey(CasdQuestions, on_delete=models.CASCADE, null=True, blank=True,related_name='casd')
    answer = models.ForeignKey(CasdAnswers, on_delete=models.CASCADE, null=True, blank=True, related_name='casd')
    selected = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"CASD - {self.result_id} - {self.score} - {self.description}"