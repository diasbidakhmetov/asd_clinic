
from users.models import User
from datetime import datetime
from datetime import date


def get_full_date(short_date):
    year = int(short_date[:2])
    month = int(short_date[2:4])
    day = int(short_date[4:6])

    current_year = datetime.now().year % 100
    century = 1900 if year > current_year else 2000

    full_year = century + year
    return f"{full_year}-{month:02d}-{day:02d}"


def format_date(date_str):
    months = {
        "01": "қаңтар", "02": "ақпан", "03": "наурыз", "04": "сәуір", "05": "мамыр", "06": "маусым",
        "07": "шілде", "08": "тамыз", "09": "қыркүйек", "10": "қазан", "11": "қараша", "12": "желтоқсан"
    }
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = f"{date_obj.day:02} {months[date_obj.strftime('%m')]} {date_obj.year}"
        return formatted_date
    except ValueError:
        return "Неверный формат даты"

def calculate_age(birth_date_str):
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    today = datetime.today()

    years = today.year - birth_date.year
    months = today.month - birth_date.month

    if months < 0:
        years -= 1
        months += 12

    return f"{years} жыл {months} ай"

def calculate_age_with_date(birth_date_str, test_date):
    if isinstance(test_date, str):
        test_date = datetime.fromisoformat(test_date.split(" ")[0])
    
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    
    years = test_date.year - birth_date.year
    months = test_date.month - birth_date.month

    if months < 0:
        years -= 1
        months += 12

    return f"{years} жыл {months} ай"


def calculate_average_age_from_db():
    """
    Возвращает средний возраст в виде строки: 'X лет Y месяцев'
    """
    today = date.today()
    birth_dates = User.objects.values_list('b_day', flat=True)

    ages = []
    for b_day in birth_dates:
        if b_day and b_day <= today:
            age_years = today.year - b_day.year - ((today.month, today.day) < (b_day.month, b_day.day))
            months = today.month - b_day.month
            if today.day < b_day.day:
                months -= 1
            if months < 0:
                months += 12
            age = age_years + months / 12
            ages.append(age)

    if not ages:
        return "Нет данных"

    avg_age = sum(ages) / len(ages)
    years = int(avg_age)
    months = int(round((avg_age - years) * 12))

    return f"{years} жас {months} ай"