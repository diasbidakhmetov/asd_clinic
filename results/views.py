from django.shortcuts import render,HttpResponseRedirect
from results.models import MChat,TestResults
from results.models import EyeResults,EyeCount
from results.models import SCQ,Cars,Atec,AtecQuestionsType,Casd
from django.shortcuts import render
from scripts.get_iin import calculate_age_with_date


def eye_results(request):
    return render(request,'results/test_result.html')

def test_results(request, test_type, result_id):
    form = request.user
    results = TestResults.objects.filter(id=result_id).last()

    age = calculate_age_with_date(str(form.b_day),str(results.date_taken))

    if test_type == 'm_chat':
        mchat = MChat.objects.filter(result_id=result_id)
        context = {
            'title': 'M-CHAT-R тестінің нәтижесі',
            'results': results,
            'mchat': mchat,
            'age':age}
        return render(request, 'results/mchat_results.html', context)

    elif test_type == 'eye_tracking':
        eye = EyeResults.objects.filter(result_id = result_id)
        eye_count = EyeCount.objects.filter(test_result = result_id)
        combined_queryset = [(result, count) for result, count in zip(eye,eye_count)]
        context = {
            'title': 'Eye Tracking тестінің нәтижесі',
            'results': results,
            'eye':eye,
            'eye_count':eye_count,
            'combined_queryset':combined_queryset,
            'age':age}
        return render(request,'results/eye_results.html',context)
    
    elif test_type == 'scq':
        scq = SCQ.objects.filter(result_id=result_id)
        context = {
            'title': 'SCQ тестінің нәтижесі',
            'results': results,
            'scq': scq,
            'age':age}
        return render(request, 'results/scq_results.html', context)
    
    elif test_type == 'cars':
        cars = Cars.objects.filter(result_id=result_id)
        context = {
            'title': 'CARS тестінің нәтижесі',
            'results': results,
            'cars': cars,
            'age':age}
        return render(request, 'results/cars_results.html', context)
    
    elif test_type == 'atec':
        atec = Atec.objects.filter(result_id=result_id)
        question_type = AtecQuestionsType.objects.all()
        context = {
            'title': 'ATEC тестінің нәтижесі',
            'results': results,
            'atec': atec,
            'question_type':question_type,
            'age':age}
        return render(request, 'results/atec_results.html', context)
    elif test_type == 'casd':
        casd = Casd.objects.filter(result_id = results)
        context = {'title':'CASD тестінің нәтижесі',
                   'results':results,
                   'casd':casd}
        return render(request, 'results/casd_results.html', context)
    else:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])