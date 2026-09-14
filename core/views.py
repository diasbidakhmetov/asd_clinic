from django.shortcuts import render


# Create your views here.
def index(request):
    context = {
        'title':'Басты бет',
        'code_name':'eye_tracking'
    }
    return render(request,'core/index.html',context)