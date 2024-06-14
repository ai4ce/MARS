import os.path
import time

import matplotlib
from nuscenes import NuScenes
from nuscenes.utils.geometry_utils import BoxVisibility, transform_matrix, view_points
from nuscenes.utils.data_classes import LidarPointCloud, RadarPointCloud, Box
import numpy as np
import open3d as o3d
from pyquaternion import Quaternion
import cv2
from tqdm import tqdm
import math
import datetime

img_width = 720
img_height = 464
img_divider = 1
frame_width = 4
font = cv2.FONT_HERSHEY_DUPLEX
color_dict = {"maisy": (200, 50, 0), "metheven": (0, 125, 250), "mike": (50, 150, 0), "mithrandir": (150, 0, 150)}
# color_dict = {"maisy": (200, 0, 0), "marinara": (0, 200, 0), "metheven": (0, 0, 200), "mike": (200, 200, 0), "mithrandir": (200, 0, 200)}
# color_dict = {"maisy": (100, 100, 0), "metheven": (200, 200, 20), "mike": (50, 200, 200), "mithrandir": (120, 0, 120)}
# color_dict = {"maisy": (0, 80, 250), "metheven": (0, 190, 80), "mike": (200, 200, 0), "mithrandir": (200, 0, 200)}
color_idx_dict = {"maisy": 0, "marinara": 1, "metheven": 2, "mike": 3, "mithrandir": 4}
v_id_dict = {"maisy": "Agent 0", "marinara": "Agent 1", "metheven": "Agent 2", "mike": "Agent 3", "mithrandir": "Agent 4"}
cmap = matplotlib.colormaps['Set1']

def transform_pcd(pcd, tran_matrix):
    '''
    :param pcd: 3*n np array (1st row x, 2nd row y, 3rd row z)
    :param tran_matrix: 4*4 transformation matrix
    :return: n*3 pcd (each row is a point [x, y, z])
    '''
    # append the pt by 1 to apply the transformation matrix
    rot = tran_matrix[:3, :3]
    trl = tran_matrix[:3, 3]
    pcd = (rot @ pcd).T + trl

    return pcd


def get_scene_tokens(nusc, first_sample_token):
    token_list = []
    sample = nusc.get('sample', first_sample_token)
    scene = nusc.get('scene', sample["scene_token"])

    nbr_samples = scene['nbr_samples']
    last_sample_token = scene['last_sample_token']
    token_list.append(first_sample_token)
    print(scene["name"])
    # vehicle = scene["name"].split("_")[-1]
    for i in range(nbr_samples - 1):
        if sample == last_sample_token:
            break
        token_list.append(sample['next'])
        sample = nusc.get('sample', sample['next'])
    # return token_list, vehicle
    return token_list


def get_scene_list(nusc):
    scene_dict = {}
    for i in range(len(nusc.scene)):
        scene = nusc.scene[i]
        first_sample_token = scene['first_sample_token']
        vehicle = scene["vehicle_list"]
        sample = nusc.get('sample', first_sample_token)
        tp = int(sample["timestamp"])
        scene_dict[first_sample_token] = [tp, vehicle]
    scene_dict = dict(sorted(scene_dict.items(), key=lambda item: item[1][0]))
    # print(scene_dict)

    return scene_dict


def img_frame(img, color):

    # print(color.astype(np.uint8))
    framed_img = cv2.copyMakeBorder(
        img,
        top=frame_width,
        bottom=frame_width,
        left=frame_width,
        right=frame_width,
        borderType=cv2.BORDER_CONSTANT,
        value=color[0].tolist()
    )

    # cv2.imshow("framed cam", framed_img)
    # cv2.waitKey()
    return framed_img


def add_tag(img, tp, vehicle, color=(0, 0, 0), fontScale=1.2, thickness=2):
    v_color = color_dict[vehicle]

    date_time = datetime.datetime.fromtimestamp(int(tp)/1000000).strftime('%Y-%m-%d %H:%M:%S.%f')
    date = date_time.split(" ")[0]
    time_s = date_time.split(" ")[1][:-3]
    h = img.shape[0]
    w = img.shape[1]
    # blank = np.ones((h, h, 3)) * 255
    blank = cv2.imread("calender_img_edge.png")
    blank = cv2.resize(blank, dsize=(h, h), interpolation=cv2.INTER_CUBIC)
    org1 = (h//8+50, (h//2))
    time_tag = cv2.putText(blank, date, org1, font, fontScale, color, thickness, cv2.LINE_AA)
    org2 = (h//8+50, (h//2)+80)
    time_tag = cv2.putText(time_tag, time_s, org2, font, fontScale, color, thickness, cv2.LINE_AA)
    org3 = (h//8+98, (h//2)+160)
    time_tag = cv2.putText(time_tag, v_id_dict[vehicle], org3, font, fontScale, v_color, thickness, cv2.LINE_AA)
    result = np.concatenate((time_tag, img), axis=1)
    return result


if __name__ == '__main__':
    root_dir = f"I:/MARS_agent_10Hz_40ms"
    nusc = NuScenes(version='v1.0', dataroot=root_dir, verbose=True)
    scene_dict = get_scene_list(nusc)
    nbr_scene = len(nusc.scene)
    # nbr_scene = 10
    # step = len(nusc.scene)//nbr_scene
    # print(f"Multi Agent has {len(nusc.scene)} scenes, showing first {nbr_scene}")

    ''' idx of scene you'd like to visualize '''
    # scene 21 has three cars, scene 30 has encounter from opposite direction
    scene_idx = 21

    scene = nusc.scene[scene_idx]
    first_token_list = list(scene_dict.keys())
    first_token = first_token_list[scene_idx]
    vehicles = scene_dict[first_token][1]
    all_token_list = get_scene_tokens(nusc, first_token)
    nbr_sample = len(all_token_list)
    nbr_vehicle = len(vehicles)

    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    ''' camera + lidar width + frame width + time tag width '''
    out0 = cv2.VideoWriter(f"{root_dir}/agent_80m_{scene_idx}.avi", fourcc, 30,
                           ((img_width * 3 + img_height * nbr_vehicle//3*2)//img_divider + frame_width*2 + img_height//img_divider -4,
                            (img_height//img_divider + frame_width*2) * nbr_vehicle))

    vis1 = o3d.visualization.Visualizer()
    vis1.create_window(
        window_name='viz',
        width=img_height // img_divider //3*2 * nbr_vehicle,
        height=(img_height // img_divider + frame_width*2) * nbr_vehicle,
        left=480,
        top=270)
    vis1.get_render_option().background_color = [1, 1, 1]
    vis1.get_render_option().point_size = 1
    vis1.get_render_option().show_coordinate_frame = True

    # empty canvas for img display
    img_canvas = np.ones(((img_height // img_divider + frame_width*2)*nbr_vehicle, img_width // img_divider * 3 + frame_width*2 + img_height // img_divider, 3)) * 255
    # empty point cloud
    pcd_obj = o3d.geometry.PointCloud()

    start_flag = True
    for i in tqdm(range(1, nbr_sample), desc=f"scene {scene_idx} of {nbr_scene}"):

        if start_flag:
            sample = nusc.get('sample', first_token)
        else:
            if sample['next'] == '':
                break
            else:
                sample = nusc.get('sample', sample['next'])

        sample_pcd_list = []
        sample_color_list = []
        # print(vehicles)
        for j in range(len(vehicles)):
            vehicle = vehicles[j]
            ''' ======================================== lidar ======================================== '''
            sample_lidar_token = sample['data'][f'LIDAR_FRONT_CENTER_{vehicle}']
            lidar_data = nusc.get('sample_data', sample_lidar_token)

            pcd_path = f"{nusc.dataroot}/{lidar_data['filename']}"
            pcd = LidarPointCloud.from_file(pcd_path).points

            ''' preserve only pts within 40 meter radius '''
            mask = np.sqrt((pcd[0, :] ** 2 + pcd[1, :] ** 2)) < 80
            pcd = pcd[:, mask][:3, :]
            # pcd = pcd[:3, :]

            ''' transform pcd from local frame to global frame '''
            ego_pose = nusc.get('ego_pose', lidar_data['ego_pose_token'])

            lidar_pose = nusc.get('calibrated_sensor', lidar_data['calibrated_sensor_token'])
            # Get global pose
            ego_pose = transform_matrix(ego_pose['translation'], Quaternion(ego_pose['rotation']), inverse=False)
            lidar_pose = transform_matrix(lidar_pose['translation'], Quaternion(lidar_pose['rotation']), inverse=False)
            global_pose = np.dot(ego_pose, lidar_pose)

            pcd = transform_pcd(pcd, global_pose)

            # color = np.array(color_dict[vehicle])
            color = np.array([color_dict[vehicle]])/255
            # print(vehicle, color)
            # color = np.array([cmap(1 / 5 * color_idx_dict[vehicle]*2)[:3]])
            colors = np.repeat(color, len(pcd), axis=0)
            sample_pcd_list.append(pcd)
            sample_color_list.append(colors)

            ''' ======================================== camera ======================================== '''
            sample_fc_token = sample['data'][f'CAM_FRONT_CENTER_{vehicle}']
            sample_fl_token = sample['data'][f'CAM_FRONT_LEFT_{vehicle}']
            sample_fr_token = sample['data'][f'CAM_FRONT_RIGHT_{vehicle}']

            fc_data = nusc.get('sample_data', sample_fc_token)
            fc_path = f"{nusc.dataroot}/{fc_data['filename']}"
            fc_img = cv2.imread(fc_path)

            fl_data = nusc.get('sample_data', sample_fl_token)
            fl_path = f"{nusc.dataroot}/{fl_data['filename']}"
            fl_img = cv2.imread(fl_path)

            fr_data = nusc.get('sample_data', sample_fr_token)
            fr_path = f"{nusc.dataroot}/{fr_data['filename']}"
            fr_img = cv2.imread(fr_path)

            h = max([fc_img.shape[0], fl_img.shape[0], fr_img.shape[0]])
            w = max([fc_img.shape[1], fl_img.shape[1], fr_img.shape[1]])

            fc_img = cv2.resize(fc_img, dsize=(w // img_divider, h // img_divider), interpolation=cv2.INTER_CUBIC)
            fl_img = cv2.resize(fl_img, dsize=(w // img_divider, h // img_divider), interpolation=cv2.INTER_CUBIC)
            fr_img = cv2.resize(fr_img, dsize=(w // img_divider, h // img_divider), interpolation=cv2.INTER_CUBIC)

            img_arr1 = [fl_img, fc_img, fr_img]

            vehicle_img = np.concatenate(img_arr1, axis=1)
            # vehicle_img2 = np.concatenate(img_arr2, axis=1)
            # vehicle_img = np.concatenate((vehicle_img1, vehicle_img2), axis=0)
            tp = lidar_data['filename'].split("/")[-1].split(".")[0]

            vehicle_img = add_tag(vehicle_img, tp, vehicle)
            # vehicle_img = img_frame(vehicle_img, color)

            num_row = vehicle_img.shape[0]
            num_col = vehicle_img.shape[1]
            img_canvas[num_row * j:num_row * (j + 1), :num_col, :] = vehicle_img
            img_canvas = img_canvas.astype(np.uint8)

        ''' new lidar scan '''
        pcd_obj.points = o3d.utility.Vector3dVector(np.concatenate(sample_pcd_list, axis=0))
        pcd_obj.colors = o3d.utility.Vector3dVector(np.concatenate(sample_color_list, axis=0))


        if start_flag:
            vis1.add_geometry(pcd_obj)
            start_flag = False
            view = vis1.get_view_control()
            view.set_zoom(0.5)
            if scene_idx == 1:
                view.translate(-50, -100)
            elif scene_idx == 2:
                view.translate(-50, -100)
            elif scene_idx == 5:
                view.translate(0, 60)
            elif scene_idx == 18:
                view.translate(50, -300)
            elif scene_idx == 21:
                view.translate(-150, 0)
            elif scene_idx == 29:
                view.translate(150, -0)
            elif scene_idx == 30:
                view.translate(0, -50)


        else:
            vis1.update_geometry(pcd_obj)

        vis1.poll_events()
        vis1.update_renderer()
        # cv2.imshow("cam", img_canvas)
        # cv2.waitKey(100)
        time.sleep(0.02)

        ''' write into video '''
        o3d_screenshot_1 = vis1.capture_screen_float_buffer()
        o3d_screenshot_1 = (255.0 * np.asarray(o3d_screenshot_1)).astype(np.uint8)
        out0.write(np.concatenate((img_canvas, o3d_screenshot_1), axis=1))

        ''' save some screenshots '''
        # if i % 5 == 0:
            # img_out_dir = f"{root_dir}/img/{scene_idx}"
            # if not os.path.exists(img_out_dir):
            #     os.makedirs(img_out_dir)
            # cv2.imwrite(f"{img_out_dir}/{i}.jpg", np.concatenate((img_canvas, o3d_screenshot_1), axis=1))
            # cv2.imwrite(f"{img_out_dir}/{i}_lidar.jpg", o3d_screenshot_1)

