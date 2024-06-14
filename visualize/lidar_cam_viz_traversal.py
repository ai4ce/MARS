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
img_divider = 4
frame_width = 4
font = cv2.FONT_HERSHEY_DUPLEX

color_dict = {"maisy": (200, 0, 0), "marinara": (0, 200, 0), "metheven": (0, 0, 200), "mike": (200, 200, 0), "mithrandir": (200, 0, 200)}
cmap = matplotlib.colormaps['tab20']

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
        vehicle = scene["name"].split("_")[-1]
        sample = nusc.get('sample', first_sample_token)
        tp = int(sample["timestamp"])
        scene_dict[first_sample_token] = [tp, vehicle]
    scene_dict = dict(sorted(scene_dict.items(), key=lambda item: item[1][0]))
    print(scene_dict)

    return scene_dict


def img_frame(img, color):
    framed_img = cv2.copyMakeBorder(
        img,
        top=frame_width,
        bottom=frame_width,
        left=frame_width,
        right=frame_width,
        borderType=cv2.BORDER_CONSTANT,
        value=color[0]*255
    )
    # print(color[0]*255)

    # cv2.imshow("framed cam", framed_img)
    # cv2.waitKey()
    return framed_img


def add_tag(img, tp, vehicle, color=(0, 0, 0), fontScale=0.4, thickness=1):
    date_time = datetime.datetime.fromtimestamp(int(tp)/1000000).strftime('%Y-%m-%d %H:%M:%S.%f')
    date = date_time.split(" ")[0]
    time_s = date_time.split(" ")[1][:-3]
    h = img.shape[0]
    w = img.shape[1]
    # blank = np.ones((h, h, 3)) * 255
    blank = cv2.imread("calender_img_edge.png")
    blank = cv2.resize(blank, dsize=(h, h), interpolation=cv2.INTER_CUBIC)
    org1 = (h//8, (h//2))
    time_tag = cv2.putText(blank, date, org1, font, fontScale, color, thickness, cv2.LINE_AA)
    org2 = (h//8, (h//2)+20)
    time_tag = cv2.putText(time_tag, time_s, org2, font, fontScale, color, thickness, cv2.LINE_AA)
    org3 = (h//8, (h//2)+38)

    time_tag = cv2.putText(time_tag, vehicle, org3, font, fontScale, color_dict[vehicle], thickness, cv2.LINE_AA)
    result = np.concatenate((time_tag, img), axis=1)
    return result


if __name__ == '__main__':
    root_dir = "K:/MARS_10Hz_location"
    location_list = [0, 1, 2, 3, 4, 5]

    for location in location_list:
        if str(location) not in os.listdir(root_dir):
            continue

        root_dir = f"K:/MARS_10Hz_location/{location}"
        nusc = NuScenes(version='v1.0', dataroot=root_dir, verbose=True)
        scene_dict = get_scene_list(nusc)

        ''' number of scenes to be visualized '''
        # nbr_scene = len(nusc.scene)
        nbr_scene = 10
        step = len(nusc.scene)//nbr_scene
        print(f"location {location} has {len(nusc.scene)} scenes, showing first {nbr_scene}")

        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out0 = cv2.VideoWriter(f"{root_dir}/../{location}_80m.avi", fourcc, 120,
                               ((img_width * 3 + img_height * 10)//img_divider + frame_width*2 + img_height//img_divider,
                                (img_height//img_divider + frame_width*2) * 10))

        vis1 = o3d.visualization.Visualizer()
        vis1.create_window(
            window_name='viz',
            width=img_height // img_divider * 10,
            height=(img_height // img_divider + frame_width * 2) * 10,
            left=480,
            top=270)
        vis1.get_render_option().background_color = [1, 1, 1]
        vis1.get_render_option().point_size = 1
        vis1.get_render_option().show_coordinate_frame = True


        ''' empty canvas for img display '''
        img_canvas = np.ones(((img_height // img_divider + frame_width*2)*10, img_width // img_divider * 3 + frame_width*2 + img_height // img_divider, 3)) * 255

        ''' open3d point cloud object '''
        pcd_obj = o3d.geometry.PointCloud()

        sample_token_dict = {}
        frame_offset_dict = {}

        start_flag = True
        first_token_list = list(scene_dict.keys())
        for i in range(nbr_scene):
            first_token = first_token_list[i*step]
            vehicle = scene_dict[first_token][1]
            sample_token_dict[str(i)] = [vehicle, get_scene_tokens(nusc, first_token)]
            frame_offset_dict[str(i)] = 0
            nbr_sample = len(sample_token_dict[str(i)])

        frame = 0
        finish_count = 0
        skip_idx = []
        batch = [0]

        last_scene_idx = max(batch)

        while True:
            location_pcd_list = []
            location_color_list = []
            img_list = []

            for idx in range(len(batch)):
                i = batch[idx]
                ''' if scene_i is finished playing, skip it '''
                if i in skip_idx:
                    continue

                scene_idx = str(i)
                offset = frame_offset_dict[scene_idx]
                ''' if last frame (frame - offset >= nbr samples) '''
                if frame - offset >= len(sample_token_dict[scene_idx][1]):
                    finish_count += 1
                    skip_idx.append(i)

                    last_scene_idx += 1
                    # if last_scene_idx < nbr_scene:
                    if last_scene_idx < nbr_scene:
                        ''' substitute the finished scene_idx with a new one '''
                        # if len(batch) == 1:
                        target_idx = batch.index(i)
                        batch[target_idx] = last_scene_idx
                        frame_offset_dict[str(last_scene_idx)] = frame
                        print(f"{frame} scene {i} finished, showing {batch}")
                    else:
                        print(f"{frame} scene {i} finished, this is the last scene")
                    continue

                sample_token = sample_token_dict[scene_idx][1][frame - offset]
                sample = nusc.get('sample', sample_token)
                # print(sample['data'])

                ''' ======================================== lidar ======================================== '''
                sample_lidar_token = sample['data']['LIDAR_FRONT_CENTER']
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
                # color = np.array([color_list[idx]]) / 255
                color = np.array([cmap(1/10 * i)[:3]])
                colors = np.repeat(color, len(pcd), axis=0)

                location_pcd_list.append(pcd)
                location_color_list.append(colors)

                ''' ======================================== camera ======================================== '''
                ''' visualize only the front three cameras '''
                sample_fc_token = sample['data']['CAM_FRONT_CENTER']
                sample_fl_token = sample['data']['CAM_FRONT_LEFT']
                sample_fr_token = sample['data']['CAM_FRONT_RIGHT']
                # sample_bc_token = sample['data']['CAM_BACK_CENTER']
                # sample_lc_token = sample['data']['CAM_SIDE_LEFT']
                # sample_rc_token = sample['data']['CAM_SIDE_RIGHT']

                fc_data = nusc.get('sample_data', sample_fc_token)
                fc_path = f"{nusc.dataroot}/{fc_data['filename']}"
                fc_img = cv2.imread(fc_path)

                fl_data = nusc.get('sample_data', sample_fl_token)
                fl_path = f"{nusc.dataroot}/{fl_data['filename']}"
                fl_img = cv2.imread(fl_path)

                fr_data = nusc.get('sample_data', sample_fr_token)
                fr_path = f"{nusc.dataroot}/{fr_data['filename']}"
                fr_img = cv2.imread(fr_path)

                # bc_data = nusc.get('sample_data', sample_bc_token)
                # bc_path = f"{nusc.dataroot}/{bc_data['filename']}"
                # bc_img = cv2.imread(bc_path)
                #
                # lc_data = nusc.get('sample_data', sample_lc_token)
                # lc_path = f"{nusc.dataroot}/{lc_data['filename']}"
                # lc_img = cv2.imread(lc_path)
                #
                # rc_data = nusc.get('sample_data', sample_rc_token)
                # rc_path = f"{nusc.dataroot}/{rc_data['filename']}"
                # rc_img = cv2.imread(rc_path)

                h = max([fc_img.shape[0], fl_img.shape[0], fr_img.shape[0]])
                w = max([fc_img.shape[1], fl_img.shape[1], fr_img.shape[1]])

                fc_img = cv2.resize(fc_img, dsize=(w//img_divider, h//img_divider), interpolation=cv2.INTER_CUBIC)
                fl_img = cv2.resize(fl_img, dsize=(w//img_divider, h//img_divider), interpolation=cv2.INTER_CUBIC)
                fr_img = cv2.resize(fr_img, dsize=(w//img_divider, h//img_divider), interpolation=cv2.INTER_CUBIC)
                # bc_img = cv2.resize(bc_img, dsize=(w, h), interpolation=cv2.INTER_CUBIC)
                # lc_img = cv2.resize(lc_img, dsize=(w, h), interpolation=cv2.INTER_CUBIC)
                # rc_img = cv2.resize(rc_img, dsize=(w, h), interpolation=cv2.INTER_CUBIC)

                img_arr1 = [fl_img, fc_img, fr_img]
                # img_arr2 = [lc_img, bc_img, rc_img]

                vehicle_img = np.concatenate(img_arr1, axis=1)
                # vehicle_img2 = np.concatenate(img_arr2, axis=1)
                # vehicle_img = np.concatenate((vehicle_img1, vehicle_img2), axis=0)
                tp = lidar_data['filename'].split("/")[-1].split(".")[0]
                vehicle = sample_token_dict[scene_idx][0]
                vehicle_img = add_tag(vehicle_img, tp, vehicle)

                vehicle_img = img_frame(vehicle_img, color)

                num_row = vehicle_img.shape[0]
                num_col = vehicle_img.shape[1]
                img_canvas[num_row*i:num_row*(i+1), :num_col, :] = vehicle_img
                img_canvas = img_canvas.astype(np.uint8)

            if finish_count == nbr_scene:
                img_out_dir = f"K:/MARS_10Hz_location/img/{location}/"
                if not os.path.exists(img_out_dir):
                    os.makedirs(img_out_dir)
                cv2.imwrite(f"{img_out_dir}/{frame}.jpg", np.concatenate((img_canvas, o3d_screenshot_1), axis=1))
                vis1.close()
                break

            if len(location_pcd_list) == 0:
                continue

            ''' new lidar scan '''
            pcd_obj.points = o3d.utility.Vector3dVector(np.concatenate(location_pcd_list, axis=0))
            pcd_obj.colors = o3d.utility.Vector3dVector(np.concatenate(location_color_list, axis=0))

            ''' new background (down-sampled) '''
            if start_flag:
                background = pcd_obj.voxel_down_sample(voxel_size=4)
                background.points = o3d.utility.Vector3dVector(background.points - np.array([0, 0, 2]))
            else:
                down_sampled = pcd_obj.voxel_down_sample(voxel_size=4)
                background.points = o3d.utility.Vector3dVector(np.concatenate((background.points, down_sampled.points - np.array([0, 0, 10])), axis=0))
                background.colors = o3d.utility.Vector3dVector(np.concatenate((background.colors, down_sampled.colors), axis=0))
                background = background.voxel_down_sample(voxel_size=1)

            ''' new full frame (background + new scan) '''
            pcd_obj.points = o3d.utility.Vector3dVector(np.concatenate((background.points, pcd_obj.points), axis=0))
            pcd_obj.colors = o3d.utility.Vector3dVector(np.concatenate((background.colors, pcd_obj.colors), axis=0))

            if start_flag:
                vis1.add_geometry(pcd_obj)
                start_flag = False
                view = vis1.get_view_control()

                ''' adjust visualize initial viewpoint as needed '''
                if location == 24:
                # # 24
                    view.set_zoom(1)
                    view.translate(-150, -100)
                # # 15
                elif location == 15:
                    view.set_zoom(1)
                    view.translate(0, -250)
                # # 59
                elif location == 59:
                    view.set_zoom(1)
                    view.translate(-150, -100)
                # # 57
                elif location == 57:
                    view.set_zoom(1)
                    view.translate(-100, 50)
                # # 3
                elif location == 3:
                    view.set_zoom(1)
                    view.translate(-0, -150)
                # 61
                elif location == 61:
                    view.set_zoom(1)
                    view.translate(200, 50)
            else:
                vis1.update_geometry(pcd_obj)

            vis1.poll_events()
            vis1.update_renderer()
            time.sleep(0.005)

            ''' write into video '''
            o3d_screenshot_1 = vis1.capture_screen_float_buffer()
            o3d_screenshot_1 = (255.0 * np.asarray(o3d_screenshot_1)).astype(np.uint8)
            out0.write(np.concatenate((img_canvas, o3d_screenshot_1), axis=1))

            ''' save some snapshots '''
            # if frame % 30 == 0:
            #     img_out_dir = f"K:/MARS_10Hz_location/img/{location}/"
            #     if not os.path.exists(img_out_dir):
            #         os.makedirs(img_out_dir)
            #     cv2.imwrite(f"{img_out_dir}/{frame}.jpg", np.concatenate((img_canvas, o3d_screenshot_1), axis=1))

            frame += 1
