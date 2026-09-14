from results.models import TestTypes

def categories_processor(request):
    return {'categories': TestTypes.objects.all()}
