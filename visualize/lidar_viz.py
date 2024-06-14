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

img_width = 256
img_height = 256
font = cv2.FONT_HERSHEY_SIMPLEX

color_list = [(255, 102, 102), (255, 255, 102), (102, 255, 102), (102, 255, 255), (178, 102, 255)]
cmap = matplotlib.colormaps['jet']

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


def get_scene_tokens(nusc, scene_index):
    token_list = []
    scene = nusc.scene[scene_index]
    nbr_samples = scene['nbr_samples']
    first_sample_token = scene['first_sample_token']
    last_sample_token = scene['last_sample_token']
    sample = nusc.get('sample', first_sample_token)
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


if __name__ == '__main__':
    location = 2
    root_dir = f"K:/MARS_10Hz_location/{location}"
    nusc = NuScenes(version='v1.0', dataroot=root_dir, verbose=True)
    nbr_scene = len(nusc.scene)
    print(f"location {location} has {nbr_scene} scenes")

    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out0 = cv2.VideoWriter(f"{root_dir}/lidar_view_traversal.avi", fourcc, 10, (img_width * 4, img_height * 4))

    vis1 = o3d.visualization.Visualizer()
    vis1.create_window(
        window_name='Ego Vehicle Segmented Scene',
        width=img_width * 4,
        height=img_height * 4,
        left=480,
        top=270)
    vis1.get_render_option().background_color = [0, 0, 0]
    vis1.get_render_option().point_size = 2
    vis1.get_render_option().show_coordinate_frame = True

    pcd_obj = o3d.geometry.PointCloud()
    '''======================================================================================='''
    # start_flag = True
    # location_pcd_list = []
    # for i in tqdm(range(nbr_scene)):
    #     scene = nusc.scene[i]
    #
    #     nbr_samples = scene['nbr_samples']
    #     first_sample_token = scene['first_sample_token']
    #     last_sample_token = scene['last_sample_token']
    #     sample = nusc.get('sample', first_sample_token)
    #
    #     while True:
    #         sample_data_token = sample['data']['LIDAR_FRONT_CENTER']
    #
    #         lidar_data = nusc.get('sample_data', sample_data_token)
    #         pcd_path = f"{nusc.dataroot}/{lidar_data['filename']}"
    #         pcd = LidarPointCloud.from_file(pcd_path).points
    #
    #         # ''' preserve only the inner 64 rings of points (total 128 rings) to reduce pcd size '''
    #         # mask = pcd[4, :] < 64
    #         # pcd = pcd[:, mask][:3, :]
    #         ''' preserve only pts within 40 meter radius '''
    #         mask = np.sqrt((pcd[0, :]**2 + pcd[1, :]**2)) < 40
    #         pcd = pcd[:, mask][:3, :]
    #
    #         ego_pose = nusc.get('ego_pose', lidar_data['ego_pose_token'])
    #         lidar_pose = nusc.get('calibrated_sensor', lidar_data['calibrated_sensor_token'])
    #         # Get global pose
    #         ego_pose = transform_matrix(ego_pose['translation'], Quaternion(ego_pose['rotation']), inverse=False)
    #         lidar_pose = transform_matrix(lidar_pose['translation'], Quaternion(lidar_pose['rotation']), inverse=False)
    #         global_pose = np.dot(ego_pose, lidar_pose)
    #
    #         pcd = transform_pcd(pcd, global_pose)
    #
    #         location_pcd_list.append(pcd)
    #
    #         pcd_obj.points = o3d.utility.Vector3dVector(pcd)
    #
    #         if start_flag:
    #             vis1.add_geometry(pcd_obj)
    #             start_flag = False
    #         else:
    #             vis1.update_geometry(pcd_obj)
    #
    #         vis1.poll_events()
    #         vis1.update_renderer()
    #         time.sleep(0.005)
    #
    #         if sample["next"] != "":
    #             sample = nusc.get('sample', sample["next"])
    #         else:
    #             break

    '''======================================================================================='''
    # sample_token_dict = {}
    # frame_offset_dict = {}
    #
    # start_flag = True
    # max_len = 0
    # for i in range(nbr_scene):
    #     sample_token_dict[str(i)] = get_scene_tokens(nusc, i)
    #     frame_offset_dict[str(i)] = 0
    #     nbr_sample = len(sample_token_dict[str(i)])
    #     if nbr_sample > max_len:
    #         max_len = nbr_sample
    #
    # frame = 0
    # finish_count = 0
    # skip_idx = []
    # batch = [0]
    #
    # last_scene_idx = max(batch)
    #
    # while True:
    # # for _ in tqdm(range(max_len)):
    #     location_pcd_list = []
    #     location_color_list = []
    #
    #     if frame % 50 == 0 and frame != 0 and len(batch) < 5:
    #         last_scene_idx += 1
    #         if last_scene_idx < nbr_scene:
    #             batch.append(last_scene_idx)
    #             frame_offset_dict[str(last_scene_idx)] = frame
    #
    #     for idx in range(len(batch)):
    #         i = batch[idx]
    #         ''' if scene_i is finished playing, skip it '''
    #         if i in skip_idx:
    #             continue
    #
    #         scene_idx = str(i)
    #         offset = frame_offset_dict[scene_idx]
    #         if frame - offset >= len(sample_token_dict[scene_idx]):
    #             finish_count += 1
    #             skip_idx.append(i)
    #
    #             last_scene_idx += 1
    #             if last_scene_idx < nbr_scene:
    #                 ''' substitute the finished scene_idx with a new one '''
    #                 target_idx = batch.index(i)
    #                 batch[target_idx] = last_scene_idx
    #                 frame_offset_dict[str(last_scene_idx)] = frame
    #                 print(f"{frame} scene {i} finished, added scene {last_scene_idx}, offset {frame_offset_dict[str(last_scene_idx)]}, showing {batch}")
    #             else:
    #                 print(f"{frame} scene {i} finished, this is the last scene")
    #             continue
    #
    #         sample_token = sample_token_dict[scene_idx][frame - offset]
    #         sample = nusc.get('sample', sample_token)
    #
    #         sample_data_token = sample['data']['LIDAR_FRONT_CENTER']
    #
    #         lidar_data = nusc.get('sample_data', sample_data_token)
    #         pcd_path = f"{nusc.dataroot}/{lidar_data['filename']}"
    #         pcd = LidarPointCloud.from_file(pcd_path).points
    #
    #         ''' preserve only pts within 40 meter radius '''
    #         mask = np.sqrt((pcd[0, :]**2 + pcd[1, :]**2)) < 40
    #         pcd = pcd[:, mask][:3, :]
    #
    #         ''' transform pcd from local frame to global frame '''
    #         ego_pose = nusc.get('ego_pose', lidar_data['ego_pose_token'])
    #         lidar_pose = nusc.get('calibrated_sensor', lidar_data['calibrated_sensor_token'])
    #         # Get global pose
    #         ego_pose = transform_matrix(ego_pose['translation'], Quaternion(ego_pose['rotation']), inverse=False)
    #         lidar_pose = transform_matrix(lidar_pose['translation'], Quaternion(lidar_pose['rotation']), inverse=False)
    #         global_pose = np.dot(ego_pose, lidar_pose)
    #
    #         pcd = transform_pcd(pcd, global_pose)
    #         color = np.array([color_list[idx]])/255
    #         colors = np.repeat(color, len(pcd), axis=0)
    #
    #         location_pcd_list.append(pcd)
    #         location_color_list.append(colors)
    #
    #     if finish_count == nbr_scene:
    #         break
    #
    #     pcd_obj.points = o3d.utility.Vector3dVector(np.concatenate(location_pcd_list, axis=0))
    #
    #     pcd_obj.colors = o3d.utility.Vector3dVector(np.concatenate(location_color_list, axis=0))
    #     if start_flag:
    #         vis1.add_geometry(pcd_obj)
    #         start_flag = False
    #     else:
    #         vis1.update_geometry(pcd_obj)
    #
    #     vis1.poll_events()
    #     vis1.update_renderer()
    #     time.sleep(0.005)
    #
    #     ''' write into video '''
    #     o3d_screenshot_1 = vis1.capture_screen_float_buffer()
    #     o3d_screenshot_1 = (255.0 * np.asarray(o3d_screenshot_1)).astype(np.uint8)
    #     out0.write(o3d_screenshot_1)
    #
    #     frame += 1

    sample_token_dict = {}
    frame_offset_dict = {}

    start_flag = True
    max_len = 0
    for i in range(nbr_scene):
        sample_token_dict[str(i)] = get_scene_tokens(nusc, i)
        frame_offset_dict[str(i)] = 0
        nbr_sample = len(sample_token_dict[str(i)])
        if nbr_sample > max_len:
            max_len = nbr_sample

    frame = 0
    finish_count = 0
    skip_idx = []
    batch = [0]

    last_scene_idx = max(batch)

    while True:
        # for _ in tqdm(range(max_len)):
        location_pcd_list = []
        location_color_list = []

        # if frame % 250 == 0 and frame != 0 and len(batch) < 5:
        #     last_scene_idx += 1
        #     if last_scene_idx < nbr_scene:
        #         batch.append(last_scene_idx)
        #         frame_offset_dict[str(last_scene_idx)] = frame

        for idx in range(len(batch)):
            i = batch[idx]
            ''' if scene_i is finished playing, skip it '''
            if i in skip_idx:
                continue

            scene_idx = str(i)
            offset = frame_offset_dict[scene_idx]
            if frame - offset >= len(sample_token_dict[scene_idx]):
                finish_count += 1
                skip_idx.append(i)

                last_scene_idx += 1
                # if last_scene_idx < nbr_scene:
                if last_scene_idx < 10:
                    ''' substitute the finished scene_idx with a new one '''
                    # if len(batch) == 1:
                    target_idx = batch.index(i)
                    batch[target_idx] = last_scene_idx
                    frame_offset_dict[str(last_scene_idx)] = frame
                    print(f"{frame} scene {i} finished, showing {batch}")
                else:
                    print(f"{frame} scene {i} finished, this is the last scene")
                continue

            sample_token = sample_token_dict[scene_idx][frame - offset]
            sample = nusc.get('sample', sample_token)

            sample_data_token = sample['data']['LIDAR_FRONT_CENTER']

            lidar_data = nusc.get('sample_data', sample_data_token)
            pcd_path = f"{nusc.dataroot}/{lidar_data['filename']}"
            pcd = LidarPointCloud.from_file(pcd_path).points

            ''' preserve only pts within 40 meter radius '''
            mask = np.sqrt((pcd[0, :] ** 2 + pcd[1, :] ** 2)) < 40
            pcd = pcd[:, mask][:3, :]

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
            # print(f"i {i}, color {1/nbr_scene * i}/1, {color}")
            colors = np.repeat(color, len(pcd), axis=0)

            location_pcd_list.append(pcd)
            location_color_list.append(colors)

        # if finish_count == nbr_scene:
        #     break
        if finish_count == 10:
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
            background.points = o3d.utility.Vector3dVector(np.concatenate((background.points, down_sampled.points - np.array([0, 0, 2])), axis=0))
            background.colors = o3d.utility.Vector3dVector(np.concatenate((background.colors, down_sampled.colors), axis=0))
            background = background.voxel_down_sample(voxel_size=1)

        ''' new full frame (background + new scan) '''
        pcd_obj.points = o3d.utility.Vector3dVector(np.concatenate((background.points, pcd_obj.points), axis=0))
        pcd_obj.colors = o3d.utility.Vector3dVector(np.concatenate((background.colors, pcd_obj.colors), axis=0))

        if start_flag:
            vis1.add_geometry(pcd_obj)
            start_flag = False
        else:
            vis1.update_geometry(pcd_obj)

        vis1.poll_events()
        vis1.update_renderer()
        time.sleep(0.005)

        ''' write into video '''
        o3d_screenshot_1 = vis1.capture_screen_float_buffer()
        o3d_screenshot_1 = (255.0 * np.asarray(o3d_screenshot_1)).astype(np.uint8)
        out0.write(o3d_screenshot_1)

        frame += 1
