import json
import base64
from io import BytesIO
from PIL import Image
import os
import glob


def tripwire_build_config(taskId, channleId, algorithm_name, data):
    config_path = "tasks/" + taskId + "/config/"

    demo_config_path = config_path + algorithm_name + "_demo.json"
    det_config_path = glob.glob(os.path.join(config_path, "yolo*_group.json"))[0]

    with open(demo_config_path, "r") as file:
        # 使用 json.load 将文件内容转换为字典
        json_data = json.load(file)

    json_data["channels"] = [json_data["channels"][0]]
    json_data["channels"][0]["url"] = data["InputSrc"]["StreamSrc"]["Address"]

    json_data["channels"][0]["sample_interval"] = data["Algorithm"][0]["DetectInterval"]
    json_data["channels"][0]["channel_id"] = channleId

    if data["InputSrc"]["StreamSrc"]["Address"][:1] == "/":
        json_data["channels"][0]["source_type"] = "VIDEO"
    elif data["InputSrc"]["StreamSrc"]["Address"][:7] == "gb28181":
        json_data["channels"][0]["source_type"] = data["InputSrc"]["StreamSrc"][
            "Address"
        ][:7].upper()
    else:
        json_data["channels"][0]["source_type"] = data["InputSrc"]["StreamSrc"][
            "Address"
        ][:4].upper()

    json_data["channels"][0]["fps"] = 25
    json_data["channels"][0]["loop_num"] = 5

    with open(demo_config_path, "w") as file:
        json.dump(json_data, file, indent=2)

    with open(det_config_path, "r") as file:
        json_data = json.load(file)
    json_data["configure"]["threshold_conf"] = (
        1.0 * data["Algorithm"][0]["threshold"] / 100.0
    )
    with open(det_config_path, "w") as file:
        json.dump(json_data, file, indent=2)

    filter_config_path = config_path + "filter.json"
    with open(filter_config_path, "r") as file:
        json_data = json.load(file)

    json_data["configure"]["rules"][0]["channel_id"] = channleId
    json_data["configure"]["rules"][0]["filters"][0]["areas"] = []
    json_data["configure"]["rules"][0]["filters"][0]["type"] = 2
    if "TrackInterval" in data["Algorithm"][0]:
        json_data["configure"]["rules"][0]["filters"][0]["alert_first_frame"] = data[
            "Algorithm"
        ][0]["TrackInterval"]
    if "AlarmInterval" in data["Algorithm"][0]:
        json_data["configure"]["rules"][0]["filters"][0]["alert_frame_skip_nums"] = (
            data["Algorithm"][0]["AlarmInterval"]
        )
    if "DetectInfos" in data["Algorithm"][0]:
        for detectinfoid in range(len(data["Algorithm"][0]["DetectInfos"])):
            # area = [
            #     {"left": i["X"], "top": i["Y"]}
            #     for i in data["Algorithm"][0]["DetectInfos"][detectinfoid]["HotArea"]
            # ]
            # json_data["configure"]["rules"][0]["filters"][0]["areas"].append(area)

            head = data["Algorithm"][0]["DetectInfos"][detectinfoid]["TripWire"][
                "LineStart"
            ]
            end = data["Algorithm"][0]["DetectInfos"][detectinfoid]["TripWire"][
                "LineEnd"
            ]
            line = [
                {"left": head["X"], "top": head["Y"]},
                {"left": end["X"], "top": end["Y"]},
            ]
            json_data["configure"]["rules"][0]["filters"][0]["areas"].append(line)

            with open(filter_config_path, "w") as file:
                json.dump(json_data, file, indent=2)

    else:
        with open(det_config_path, "r") as file:
            json_data = json.load(file)
        if "roi" in json_data["configure"].keys():
            del json_data["configure"]["roi"]
        with open(det_config_path, "w") as file:
            json.dump(json_data, file, indent=2)

    return demo_config_path


def tripwire_trans_json(json_data, task_id, Type):
    results = {}
    frame_id = int(json_data["mFrame"]["mFrameId"])
    results["FrameIndex"] = frame_id

    src_base64 = json_data["mFrame"]["mSpData"]
    results["SceneImageBase64"] = src_base64
    results["AnalyzeEvents"] = []
    results["TaskID"] = str(task_id)
    image_data = base64.b64decode(src_base64)
    # 使用Pillow打开图片
    image = Image.open(BytesIO(image_data))
    width, height = image.size

    boxes = []
    if "mTrackedObjectMetadatas" in json_data.keys():
        for indx in range(len(json_data["mDetectedObjectMetadatas"])):
            tmp = json_data["mDetectedObjectMetadatas"][indx]

            result = {}
            x1, y1 = tmp["mBox"]["mX"], tmp["mBox"]["mY"]
            x2 = x1 + tmp["mBox"]["mWidth"]
            y2 = y1 + tmp["mBox"]["mHeight"]
            boxes.append((x1, y1, x2, y2))
            crop_box = crop_target_square(width, height, x1, y1, x2, y2)
            cropped_image = image.crop(crop_box)

            buffer = BytesIO()
            cropped_image.save(buffer, format="JPEG")  # 选择格式
            # 将buffer内容转换为base64格式
            buffer.seek(0)
            small_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
            result["ImageBase64"] = small_image
            result["Box"] = {
                "LeftTopY": y1,
                "RightBtmY": y2,
                "LeftTopX": x1,
                "RightBtmX": x2,
            }
            result["Type"] = Type
            results["AnalyzeEvents"].append(result)
    return results


def crop_target_square(width, height, x1, y1, x2, y2):
    # 计算目标正方形的中心坐标
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    # 计算正方形的一半边长
    half_size = max(center_x - x1, x2 - center_x, center_y - y1, y2 - center_y)

    # 计算正方形的边界
    left = max(0, center_x - half_size - 20)
    top = max(0, center_y - half_size - 20)
    right = min(width, center_x + half_size + 20)
    bottom = min(height, center_y + half_size + 20)

    # 返回新的四个坐标
    return left, top, right, bottom
