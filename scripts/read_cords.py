import json
import numpy as np
import cv2
import os
from django.conf import settings


def draw_line(data, name, folder_name):

    test_image_dir = "static/images/test_images"
    test_image_files = [f for f in os.listdir(test_image_dir) if f.lower().endswith(('.jpeg', '.jpg', '.png'))]

    test_num_images = len(test_image_files)
    print("Length of test images folders", test_num_images)
    

    with open(f"static/screen_size/screen_size.json", 'r', encoding='utf-8') as f:
        screen_size = json.load(f)
    
    print(" Size of screen: ",screen_size)
    img_paths = []
    temp = 1
    save_dir = f'static/result_images/{name}/{folder_name}'
    
    os.makedirs(save_dir, exist_ok=True)

    while True:
        x_data, y_data = [], []
        key = f'/static/images/test_images/test_image_{temp}.jpeg'
        
        if key not in data:
            print(f"Ключ {key} отсутствует в JSON. Прекращаем работу.")
            break

        image = cv2.imread(key[1:])
        
        if image is None:
            print(f"Файл {key} не найден. Прекращаем работу.")
            break
        
        img = cv2.resize(image, (screen_size['width'], screen_size['height']))
        for coord in data[key]:
            x_data.append(coord['x'])
            y_data.append(coord['y'])

        for i in range(len(x_data) - 1):
            pt1, pt2 = (int(x_data[i]), int(y_data[i])), (int(x_data[i+1]), int(y_data[i+1]))
            cv2.line(img, pt1, pt2, (0, 255, 0), 2)
        
        save_path = f'{save_dir}/{name}_eye_lines_v{temp}.jpg'
        img_paths.append(save_path)
        cv2.imwrite(save_path, img)
        print(f"Изображение сохранено: {save_path}")
        
        temp += 1

        if temp == test_num_images+1:
            break

    return img_paths

def coords_count(arr, bound, zone_type):
    arr = np.array(arr)
    if zone_type in ['bottom', 'right']:
        return [np.sum(arr > bound), np.sum(arr <= bound)]
    elif zone_type in ['top', 'left']:
        return [np.sum(arr < bound), np.sum(arr >= bound)]
    return [0, 0]


def make_data(coords_list, coords_axis):
    if not coords_list:
        return np.array([])
    return np.array([point[coords_axis] for point in coords_list])


def eye_tracking_result(data,name,folder):
    with open('static/screen_size/screen_size.json', 'r', encoding='utf-8') as f:
        screen_size = json.load(f)

    x_mean, y_mean = screen_size['width'] // 2, screen_size['height'] // 2
    results = []
    number_result = 0
    image_zones = ['bottom', 'right', 'top', 'left']
    image_paths = [f'/static/images/test_images/test_image_{i}.jpeg' for i in range(1, 11)]

    zone_counts = {}

    for i, image in enumerate(image_paths):
        if image not in data:
            print(f"Данные для {image} отсутствуют. Пропускаем.")
            continue

        zone_type = image_zones[i % 4]
        axis = 'y' if zone_type in ['bottom', 'top'] else 'x'
        bound = y_mean if zone_type in ['bottom', 'top'] else x_mean

        coord_data = make_data(data[image], axis)
        interest_count, neutral_count = coords_count(coord_data, bound, zone_type)

        zone_counts[image] = {
            'interest_zone': int(interest_count),
            'neutral_zone': int(neutral_count)
        }

        if interest_count > neutral_count:
            results.append('Зона интереса')
            number_result += 1
        else:
            results.append('Нейтральная зона')

    if number_result >= 8:
        final_result = 'Аутизм белгілері анықталмады'
        result_index = 1
    elif number_result >= 6:
        final_result = 'Аутизм белгілері анықталмады, бірақ тестті тағы бір рет өту ұсынылады'
        result_index = 2
    else:
        final_result = 'Аутизм белгілері бар'
        result_index = 3

    output_path = f'./eye_data/eye_tracking_coords/{name}/{folder}/eye_tracking_results.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(zone_counts, f, ensure_ascii=False, indent=4)

    return final_result, zone_counts
