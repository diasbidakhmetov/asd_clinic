import os
import json
from datetime import datetime
from users.models import User
from scripts import read_cords
from django.urls import reverse
from django.conf import settings
from django.core.files import File
from collections import defaultdict
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Prefetch
from scripts.read_cords import draw_line
from autizm_tests.models import TestGuideSite
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from results.models import SCQ,SCQQuestions,SCQDescriptions
from results.models import EyeDescription,EyeCount,TestImage
from results.models import Cars,CarsAnswers,CarsDescriptions,CarsQuestions
from results.models import Casd,CasdAnswers,CasdDescriptions,CasdQuestions
from results.models import Atec,AtecQuestions,AtecDescriptions,AtecQuestionsType,AtecAnswers
from results.models import TestResults, TestTypes, EyeResults, MChatQuestions, MChatRiskLevel,MChat


def test_guide(request,code_name):
    test_type = TestTypes.objects.get(code_name=code_name)
    guide = TestGuideSite.objects.filter(test_type=test_type)
    context = {'title':'Тесттер','guide':guide,'code_name':code_name}
    if code_name == 'eye_tracking':
        return render(request, 'autizm_tests/eye_tracking.html', context)
    else:
        return render(request, 'autizm_tests/test_guide.html', context)

def tests(request,code_name):
    if code_name == 'm_chat':
        questions = list(MChatQuestions.objects.values_list('name', flat=True))
        context = {
            'title': 'M-CHAT-R',
            'questions_json': json.dumps(questions, ensure_ascii=False),
        }
        return render(request, 'autizm_tests/m_chat.html', context)
    elif code_name == 'scq':
        questions = list(SCQQuestions.objects.values_list('name', flat=True))
        context = {
            'title': 'SCQ',
            'questions_json': json.dumps(questions, ensure_ascii=False),
        }
        return render(request, 'autizm_tests/scq.html', context)
    elif code_name == 'eye_tracking':
        return render(request, 'autizm_tests/eye_tracking.html')
    elif code_name == 'cars':

        question = list(CarsQuestions.objects.order_by('number').values_list('name', flat=True).distinct())
        description = list(CarsDescriptions.objects.values_list('name', flat=True))

        answers = CarsAnswers.objects.exclude(name__in=[1.5, 2.5, 3.5]).order_by('number', 'score').values("number", "name", "score")

        grouped_answers = defaultdict(list)
        for answer in answers:
            grouped_answers[answer["number"]].append({
                "name": answer["name"],
                "score": answer["score"]
            })

        result = {"answers": [group for group in grouped_answers.values()]}
        context = {'title':'CARS',
                'question':json.dumps(question, ensure_ascii=False),
                'answer':json.dumps(result, ensure_ascii=False),
                'description':json.dumps(description, ensure_ascii=False)}
        
        return render(request, "autizm_tests/cars.html", context)
    
    elif code_name == 'atec':
        question_types = AtecQuestionsType.objects.all()
        questions_by_type = {q_type.name: AtecQuestions.objects.filter(type=q_type) for q_type in question_types}
        context =  {
            "title": "ATEC",
            "questions_by_type": questions_by_type,
            "question_types": question_types
        }
        return render(request, "autizm_tests/atec.html",context)
    
    elif code_name == 'casd':
        descriptions = list(
                CasdDescriptions.objects.all().values('number', 'name')
            )
        questions = CasdQuestions.objects.prefetch_related(
            Prefetch('casdanswers_set', queryset=CasdAnswers.objects.all())
        )

        questions_list = []
        for q in questions:
            questions_list.append({
                'id': q.id,
                'number': q.number,
                'name': q.name,
                'answers': [{'id': a.id, 'name': a.name} for a in q.casdanswers_set.all()]
            })
        context = {
            'title': 'CASD',
            'questions_json': questions_list,
            'description':descriptions,
        }
        return render(request, 'autizm_tests/casd.html', context)


@csrf_exempt  
def submit_mchat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            try:    
                useriin = request.user.iin
                user = User.objects.get(iin=useriin)
            except User.DoesNotExist:
                return JsonResponse({"error": "Пользователь с таким ИИН не найден"}, status=400)

            try:
                test_type = TestTypes.objects.get(code_name="m_chat")
            except TestTypes.DoesNotExist:
                return JsonResponse({"error": "Тип теста 'M-CHAT' не найден"}, status=400)

            test_result = TestResults.objects.create(iin=user, test_type=test_type)
            
            try:
                risk_level = MChatRiskLevel.objects.get(name=data["riskLevel"])
            except MChatRiskLevel.DoesNotExist:
                return JsonResponse({"error": "Уровень риска не найден"}, status=400)

            for item in data["answers"]:
                try:
                    question = MChatQuestions.objects.get(number=item["question"])
                    MChat.objects.create(
                        result_id=test_result,
                        score=data["score"],
                        risk_level=risk_level,
                        question=question,
                        answer=item["answer"]
                    )
                except MChatQuestions.DoesNotExist:
                    return JsonResponse({"error": f"Вопрос с ID {item['question']} не найден"}, status=400)

            redirect_url = reverse("autizm_tests:temp_test_results")  

            return JsonResponse({
                "message": "Данные успешно сохранены!",
                "redirect_url": redirect_url
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Ошибка в формате JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

@csrf_exempt
def save_gaze_data(request):
    if request.method == "POST":
        try:
            raw_data = request.body.decode("utf-8")
            data = json.loads(raw_data)
            gaze_data_by_image = data.get("gazeDataByImage", {})
            if not gaze_data_by_image:
                return JsonResponse({"error": "No gaze data provided"}, status=400)
            try:
                user = User.objects.get(iin=request.user.iin)
            except User.DoesNotExist:
                return JsonResponse({"error": "Пользователь с таким ИИН не найден"}, status=400)
            try:
                test_type = TestTypes.objects.get(code_name="eye_tracking")
            except TestTypes.DoesNotExist:
                return JsonResponse({"error": "Тип теста 'Eye Tracking' не найден"}, status=400)
            test_result = TestResults.objects.create(iin=user, test_type=test_type)
            if isinstance(test_result.date_taken, str):
                date_of_taken = datetime.fromisoformat(test_result.date_taken.replace(" +00:00", ""))
            else:
                date_of_taken = test_result.date_taken
            safe_timestamp = date_of_taken.strftime("%Y-%m-%d_%H-%M-%S")
            desc, coords_count = read_cords.eye_tracking_result(gaze_data_by_image,request.user.iin,safe_timestamp)
            result_images = draw_line(gaze_data_by_image,request.user.iin,safe_timestamp)
            try:
                description = EyeDescription.objects.get(name=desc)
            except EyeDescription.DoesNotExist:
                return JsonResponse({"error": "Уровень риска не найден"}, status=400) 

            try:
                for item in result_images:
                    file_path = item
                    if not os.path.exists(file_path):
                        return JsonResponse({"error": f"Файл {file_path} не найден"}, status=500)

                    with open(file_path, "rb") as img_file:
                        try:
                            EyeResults.objects.create(
                                result_id=test_result,
                                description=description,
                                coords=json.dumps(gaze_data_by_image),
                                result_image=File(img_file, name=file_path)
                            )
                        except Exception as e:
                            print("Ошибка при создании EyeResults:", e)
                            return JsonResponse({"error": f"Ошибка при сохранении EyeResults: {str(e)}"}, status=500)

            except Exception as e:
                return JsonResponse({"error": f"Ошибка при сохранении EyeResults: {str(e)}"}, status=500)

            try:
                for idx, (key, value) in enumerate(coords_count.items(), start=1):
                    try:
                        test_image = TestImage.objects.get(number=idx)
                        EyeCount.objects.create(
                            neitral=value["neutral_zone"],
                            social=value["interest_zone"],
                            image=test_image,
                            test_result=test_result
                        )
                    except TestImage.DoesNotExist:
                        print(f"TestImage с id={idx} не найден, пропускаем...")
            except Exception as e:
                print("Ошибка при создании EyeCount:", e)
                return JsonResponse({"error": f"Ошибка при сохранении EyeCount: {str(e)}"}, status=500)


            redirect_url = reverse("autizm_tests:temp_test_results")

            return JsonResponse({
                "message": "Данные успешно сохранены!",
                "redirect_url": redirect_url
            }, status=200)


        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def save_screen_size(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            screen_width = data.get("width")
            screen_height = data.get("height")
            return JsonResponse({"message": "Размер экрана сохранён!"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Ошибка в формате JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

def train_model(request):
    return render(request, 'autizm_tests/train_model.html')

MODEL_DIR = os.path.join(settings.BASE_DIR, "eye_data")
MODEL_PATH = os.path.join(MODEL_DIR, "model.json")

@csrf_exempt
def save_model(request):
    """Сохранение модели WebGazer."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            model = data.get("model")

            if model:
                os.makedirs(MODEL_DIR, exist_ok=True)
                with open(MODEL_PATH, "w") as file:
                    json.dump(model, file)

                return JsonResponse({"message": "Модель сохранена"}, status=200)

            return JsonResponse({"message": "Ошибка: нет данных для сохранения"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Ошибка обработки JSON"}, status=400)

    return JsonResponse({"message": "Метод не разрешён"}, status=405)

@csrf_exempt
def load_model(request):
    """Загрузка модели WebGazer."""
    if request.method == "GET":
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "r") as file:
                model = json.load(file)
            return JsonResponse({"model": model}, status=200)

        return JsonResponse({"message": "Нет сохраненной модели"}, status=404)

    return JsonResponse({"message": "Метод не разрешён"}, status=405)

SCREEN_SIZE_PATH = os.path.join(settings.BASE_DIR, "static/screen_size")

@csrf_exempt
@require_POST
def save_screen_size(request):
    try:
        data = json.loads(request.body)
        file_path = os.path.join(SCREEN_SIZE_PATH, "screen_size.json")

        os.makedirs(SCREEN_SIZE_PATH, exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        return JsonResponse({"message": "Размер экрана сохранён", "data": data})
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Неверный формат JSON"}, status=400)

@csrf_exempt
def submit_scq(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            try:    
                useriin = request.user.iin
                user = User.objects.get(iin=useriin)
            except User.DoesNotExist:
                return JsonResponse({"error": "Пользователь с таким ИИН не найден"}, status=400)

            try:
                test_type = TestTypes.objects.get(code_name="scq")
            except TestTypes.DoesNotExist:
                return JsonResponse({"error": "Тип теста 'Әлеуметтік-коммуникативтік сауалнама (SCQ)' не найден"}, status=400)

            test_result = TestResults.objects.create(iin=user, test_type=test_type)

            try:
                description = SCQDescriptions.objects.get(name=data["description"])
            except SCQDescriptions.DoesNotExist:
                return JsonResponse({"error": "Уровень риска не найден"}, status=400)

            for item in data["answers"]:
                try:
                    question = SCQQuestions.objects.get(number=item["question"])
                    SCQ.objects.create(
                        result_id=test_result,
                        score=data["score"],
                        description=description,
                        question=question,
                        answer=item["answer"]
                    )
                except SCQQuestions.DoesNotExist:
                    return JsonResponse({"error": f"Вопрос с ID {item['question']} не найден"}, status=400)
                
            redirect_url = reverse("autizm_tests:temp_test_results")  

            return JsonResponse({
                "message": "Данные успешно сохранены!",
                "redirect_url": redirect_url
            }, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Ошибка в формате JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

@csrf_exempt
def save_cars_results(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            total_score = data.get("totalScore", 0)
            answers = data.get("answers", [])
            diagnosis_text = data.get("diagnosis", "")
            
            try:    
                useriin = request.user.iin
                user = User.objects.get(iin=useriin)
            except User.DoesNotExist:
                return JsonResponse({"error": "Пользователь с таким ИИН не найден"}, status=400)

            try:
                test_type = TestTypes.objects.get(name="CARS")
            except TestTypes.DoesNotExist:
                return JsonResponse({"error": "Тип теста 'CARS' не найден"}, status=400)

            test_result = TestResults.objects.create(iin=user, test_type=test_type)

            diagnosis_obj = CarsDescriptions.objects.get(number=diagnosis_text)

            for answer in answers:
                question_text = answer["question"]
                answer_text = answer["answer"]
                score = answer["score"]

                question_obj = CarsQuestions.objects.filter(name=question_text).first()
                if not question_obj:
                    question_obj = CarsQuestions.objects.create(name=question_text)
                
                answer_obj, _ = CarsAnswers.objects.get_or_create(name=answer_text, score=score)

                Cars.objects.create(
                    result_id=test_result,
                    score=str(score),
                    total=str(total_score),
                    description=diagnosis_obj,
                    question=question_obj,
                    answer=answer_obj
                )

            redirect_url = reverse("autizm_tests:temp_test_results")

            return JsonResponse({
                "message": "Данные успешно сохранены!",
                "redirect_url": redirect_url
            }, status=201)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@csrf_exempt
def save_atec_results(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            total_score = data["total_score"]
            description = data["description"]
            answers = data["answers"]

            try:    
                useriin = request.user.iin
                user = User.objects.get(iin=useriin)
            except User.DoesNotExist:
                return JsonResponse({"error": "Пользователь с таким ИИН не найден"}, status=400)

            try:
                test_type = TestTypes.objects.get(code_name="atec")
            except TestTypes.DoesNotExist:
                return JsonResponse({"error": "Тип теста 'ATEC' не найден"}, status=400)

            test_result = TestResults.objects.create(iin=user, test_type=test_type)
        
            description_obj = AtecDescriptions.objects.get(name = description) 
        
            for answer in answers:
                answer_text = answer["answer"]
                question_obj = AtecQuestions.objects.get(name = answer['question_name'])
                answer_obj = AtecAnswers.objects.get(name=answer_text)
                Atec.objects.create(
                    result_id=test_result,
                    score=str(answer["score"]),
                    question=question_obj,
                    total=str(77),
                    description =description_obj,
                    answer=answer_obj
                )
            redirect_url = reverse("autizm_tests:temp_test_results")

            return JsonResponse({
                "message": "Данные успешно сохранены!",
                "redirect_url": redirect_url
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

def eye_tracking_result(request):
    return render(request, 'autizm_tests/eye_tracking_result.html')


@csrf_exempt
def casd_result_submit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        description = data['diagnosis']
        score = data['score']

        try:    
            useriin = request.user.iin
            user = User.objects.get(iin=useriin)
        except User.DoesNotExist:
            return JsonResponse({"error": "Пользователь с таким ИИН не найден"}, status=400)
        try:
            test_type = TestTypes.objects.get(code_name="casd")
        except TestTypes.DoesNotExist:
            return JsonResponse({"error": "Тип теста 'CASD' не найден"}, status=400)

        test_result = TestResults.objects.create(iin=user, test_type=test_type)
        
        description_obj = CasdDescriptions.objects.get(name = description)

        for item in data['results']:
            question = CasdQuestions.objects.get(id=item['question_id'])
            
            if item['answers']:
                for answer in item['answers']:
                    Casd.objects.create(
                        result_id=test_result,
                        score = score,
                        description = description_obj,
                        answer = CasdAnswers.objects.get(name=answer),
                        selected = item['selected'],
                        question=question
                    )
            else:
                Casd.objects.create(
                    result_id=test_result,
                    score = score,
                    description = description_obj,
                    selected = item['selected'],
                    question=question
                    )

        redirect_url = reverse("autizm_tests:temp_test_results")
        return JsonResponse({
                "message": "Данные успешно сохранены!",
                "redirect_url": redirect_url
            }, status=201)
    return JsonResponse({'error': 'Invalid method'}, status=405)


def temp_test_results(request):
    useriin = request.user.iin
    user = User.objects.get(iin=useriin)
    result = TestResults.objects.filter(iin = user).last()
    test_type = result.test_type.code_name

    if test_type == 'm_chat':
        mchat = MChat.objects.filter(result_id=result)
        context = {'title':'M-CHAT',
                   'results':result,
                   'mchat':mchat}
        return render(request, 'results/mchat_results.html',context)
    elif test_type == 'scq':
        scq = SCQ.objects.filter(result_id=result)
        context = {'title':'SCQ',
                   'results':result,
                   'scq':scq}
        return render(request, 'results/scq_results.html',context)
    elif test_type == 'cars':
        cars = Cars.objects.filter(result_id=result)
        context = {'title':'CARS',
                   'results':result,
                   'cars':cars}
        return render(request, 'results/cars_results.html',context)
    elif test_type == 'atec':
        atec = Atec.objects.filter(result_id=result)
        question_type = AtecQuestionsType.objects.all()
        context = {
            'title': 'ATEC тестінің нәтижесі',
            'results': result,
            'atec': atec,
            'question_type':question_type}
        return render(request, 'results/atec_results.html', context)
    elif test_type == 'eye_tracking':
        eye = EyeResults.objects.filter(result_id = result)
        eye_count = EyeCount.objects.filter(test_result = result)
        combined_queryset = [(result, count) for result, count in zip(eye,eye_count)]
        context = { 
            'title': 'Eye Tracking тестінің нәтижесі',
            'results': result,
            'eye':eye,
            'eye_count':eye_count,
            'combined_queryset':combined_queryset}
        return render(request,'results/eye_results.html',context)
    elif test_type == 'casd':
        casd = Casd.objects.filter(result_id = result)
        context = {'title':'CASD тестінің нәтижесі',
                   'results':result,
                   'casd':casd}
        return render(request,'results/casd_results.html',context)
    