from django.db import models
from results.models import TestTypes

class TestGuideSite(models.Model):
    name = models.TextField()
    test_type = models.ForeignKey(TestTypes, on_delete=models.CASCADE,default=1)

    def __str__(self):
        return f"{self.test_type} - описание теста"

