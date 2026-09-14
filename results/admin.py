from django.contrib import admin
from results.models import SCQ,SCQDescriptions,SCQQuestions
from results.models import MChatRiskLevel,MChatQuestions,MChat
from results.models import Cars,CarsAnswers,CarsDescriptions,CarsQuestions
from results.models import Casd,CasdAnswers,CasdDescriptions,CasdQuestions
from results.models import Atec,AtecAnswers,AtecDescriptions,AtecQuestions,AtecQuestionsType
from results.models import TestTypes,TestResults,EyeDescription,TestImage,EyeCount,EyeResults
# Register your models here.

admin.site.register(EyeCount)
admin.site.register(TestTypes)
admin.site.register(TestImage)
admin.site.register(EyeResults)
admin.site.register(TestResults)
admin.site.register(EyeDescription)

admin.site.register(MChat)
admin.site.register(MChatRiskLevel)
admin.site.register(MChatQuestions)

admin.site.register(SCQ)
admin.site.register(SCQQuestions)
admin.site.register(SCQDescriptions)

admin.site.register(Cars)
admin.site.register(CarsAnswers)
admin.site.register(CarsQuestions)
admin.site.register(CarsDescriptions)

admin.site.register(Atec)
admin.site.register(AtecAnswers)
admin.site.register(AtecQuestions)
admin.site.register(AtecDescriptions)
admin.site.register(AtecQuestionsType)


admin.site.register(Casd)
admin.site.register(CasdAnswers)
admin.site.register(CasdQuestions)
admin.site.register(CasdDescriptions)