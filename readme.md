# Open MARS Dataset
![teaser](https://github.com/ai4ce/MARS/assets/105882130/963f7ea2-0590-42dc-9ddd-22a9b57f947c)

<br/>

## Welcome to the tutorial of Open MARS Dataset!

Our paper has been accepted on CVPR 2024 🎉🎉🎉

Checkout our [project website](https://ai4ce.github.io/MARS/) for demo videos.
Codes to reproduce the videos are available in `/visualize` folder of `main` branch.

<br/>

## Intro
### The MARS dataset is collected with a fleet of autonomous vehicles from [MayMobility](https://maymobility.com/).

Our dataset uses the same structure as the [NuScenes](https://www.nuscenes.org/nuscenes) Dataset:

- Multitraversal: each location is saved as one NuScenes object, and each traversal is one scene.
- Multiagent: the whole set is a NuScenes object, and each multiagent encounter is one scene.

<br/>

## Download
Both Multiagent and Multitraversal subsets are now available for [download on huggingface](https://huggingface.co/datasets/ai4ce/MARS). 

<br/>

## Overview
This tutorial explains how the NuScenes structure works in our dataset, including how you may access a scene and query its samples of sensor data.

- [Devkit Initialization](#initialization)
  - [Multitraversal](#load-multitraversal)
  - [Multiagent](#load-multiagent)
- [Scene](#scene)
- [Sample](#sample)
- [Sample Data](#sample-data)
  - [Sensor Names](#sensor-names)
  - [Camera](#camera-data)
  - [LiDAR](#lidar-data)
  - [IMU](#imu-data)
  - [Ego & Sensor Pose](#vehicle-and-sensor-pose)
- [LiDAR-Image projection](#lidar-image-projection)

<br/>

## Initialization
First, install `nuscenes-devkit` following NuScenes's repo tutorial, [Devkit setup section](https://github.com/nutonomy/nuscenes-devkit?tab=readme-ov-file#devkit-setup). The easiest way is install via pip:
```
pip install nuscenes-devkit
```

Import NuScenes devkit:
```
from nuscenes.nuscenes import NuScenes
```

#### Load Multitraversal 
loading data of location 10:
```
# The "version" variable is the name of the folder holding all .json metadata tables.
location = 10
nusc = NuScenes(version='v1.0', dataroot=f'/MARS_multitraversal/{location}', verbose=True)
```

#### Load Multiagent
loading data for the full set:
```
nusc = NuScenes(version='v1.0', dataroot=f'/MARS_multiagent', verbose=True)
```

<br/>

## Scene
To see all scenes in one set (one location of the Multitraversal set, or the whole Multiagent set):
```
print(nusc.scene)
```
Output:
```
[{'token': '97hitl8ya1335v8zkixvsj3q69tgx801', 'nbr_samples': 611, 'first_sample_token': 'udrq868482482o88p9r2n8b86li7cfxx', 'last_sample_token': '7s5ogk8m9id7apixkqoh3rep0s9113xu', 'name': '2023_10_04_scene_3_maisy', 'intersection': 10, 'err_max': 20068.00981996727},
{'token': 'o858jv3a464383gk9mm8at71ai994d3n', 'nbr_samples': 542, 'first_sample_token': '933ho5988jo3hu848b54749x10gd7u14', 'last_sample_token': 'os54se39x1px2ve12x3r1b87e0d7l1gn', 'name': '2023_10_04_scene_4_maisy', 'intersection': 10, 'err_max': 23959.357933579337},
{'token': 'xv2jkx6m0o3t044bazyz9nwbe5d5i7yy', 'nbr_samples': 702, 'first_sample_token': '8rqb40c919d6n5cd553c3j01v178k28m', 'last_sample_token': 'skr79z433oyi6jljr4nx7ft8c42549nn', 'name': '2023_10_04_scene_6_mike', 'intersection': 10, 'err_max': 27593.048433048432},
{'token': '48e90c7dx401j97391g6549zmljbg0hk', 'nbr_samples': 702, 'first_sample_token': 'ui8631xb2in5la133319c5301wvx1fib', 'last_sample_token': 'xrns1rpma4p00hf39305ckol3p91x59w', 'name': '2023_10_04_scene_9_mike', 'intersection': 10, 'err_max': 24777.237891737892},
...
]

```

The scenes can then be retrieved by indexing:
```
num_of_scenes = len(nusc.scene)
my_scene = nusc.scene[0]    # scene at index 0, which is the first scene of this location
print(first_scene)
```
Output:
```
{'token': '97hitl8ya1335v8zkixvsj3q69tgx801',
'nbr_samples': 611,
'first_sample_token': 'udrq868482482o88p9r2n8b86li7cfxx',
'last_sample_token': '7s5ogk8m9id7apixkqoh3rep0s9113xu',
'name': '2023_10_04_scene_3_maisy',
'intersection': 10,
'err_max': 20068.00981996727}
```
- `nbr_samples`: number of samples (frames) of this scene.
- `name`: name of the scene, including its date and name of the vehicle it is from (in this example, the data is from Oct. 4th 2023, vehicle maisy).
- `intersection`: location index. 
- `err_max`: maximum time difference (in millisecond) between camera images of a same frame in this scene.

<br/>

## Sample
Get the first sample (frame) of one scene:
```
first_sample_token = my_scene['first_sample_token']    # get sample token
my_sample = nusc.get('sample', first_sample_token)    # get sample metadata
print(my_sample)
```

Output:
```
{'token': 'udrq868482482o88p9r2n8b86li7cfxx',
'timestamp': 1696454482883182,
'prev': '',
'next': 'v15b2l4iaq1x0abxr45jn6bi08j72i01',
'scene_token': '97hitl8ya1335v8zkixvsj3q69tgx801',
'data': {
  'CAM_FRONT_CENTER': 'q9e0pgk3wiot983g4ha8178zrnr37m50',
  'CAM_FRONT_LEFT': 'c13nf903o913k30rrz33b0jq4f0z7y2d',
  'CAM_FRONT_RIGHT': '67ydh75sam2dtk67r8m3bk07ba0lz3ib',
  'CAM_BACK_CENTER': '1n09qfm9vw65xpohjqgji2g58459gfuq',
  'CAM_SIDE_LEFT': '14up588181925s8bqe3pe44d60316ey0',
  'CAM_SIDE_RIGHT': 'x95k7rvhmxkndcj8mc2821c1cs8d46y5',
  'LIDAR_FRONT_CENTER': '13y90okaf208cqqy1v54z87cpv88k2qy',
  'IMU_TOP': 'to711a9v6yltyvxn5653cth9w2o493z4'
},
'anns': []}
```
- `prev`: token of the previous sample.
- `next`': token of the next sample.
- `data`: dict of data tokens of this sample's sensor data.
- `anns`: empty as we do not have annotation data at this moment.

<br/>

## Sample Data
### Sensor Names
Our sensor names are different from NuScenes' sensor names. It is important that you use the correct name when querying sensor data. Our sensor names are:
```
['CAM_FRONT_CENTER',
'CAM_FRONT_LEFT',
'CAM_FRONT_RIGHT',
'CAM_BACK_CENTER',
'CAM_SIDE_LEFT',
'CAM_SIDE_RIGHT',
'LIDAR_FRONT_CENTER',
'IMU_TOP']
```

---
### Camera Data
All image data are already undistorted. 

To load a piece data, we start with querying its `sample_data` dictionary object from the metadata:
```
sensor = 'CAM_FRONT_CENTER'
sample_data_token = my_sample['data'][sensor]
FC_data = nusc.get('sample_data', sample_data_token)
print(FC_data)
```
Output: 
```
{'token': 'q9e0pgk3wiot983g4ha8178zrnr37m50',
'sample_token': 'udrq868482482o88p9r2n8b86li7cfxx',
'ego_pose_token': 'q9e0pgk3wiot983g4ha8178zrnr37m50',
'calibrated_sensor_token': 'r5491t78vlex3qii8gyh3vjp0avkrj47',
'timestamp': 1696454482897062,
'fileformat': 'jpg',
'is_key_frame': True,
'height': 464,
'width': 720,
'filename': 'sweeps/CAM_FRONT_CENTER/1696454482897062.jpg',
'prev': '',
'next': '33r4265w297khyvqe033sl2r6m5iylcr',
'sensor_modality': 'camera',
'channel': 'CAM_FRONT_CENTER'}
```
- `ego_pose_token`: token of vehicle ego pose at the time of this sample.
- `calibrated_sensor_token`: token of sensor calibration information (e.g. distortion coefficient, camera intrinsics, sensor pose & location relative to vehicle, etc.).
- `is_key_frame`: disregard; all images have been marked as key frame in our dataset.
- `height`: image height in pixel
- `width`: image width in pixel
- `filename`: image directory relative to the dataset's root folder
- `prev`: previous data token for this sensor
- `next`: next data token for this sensor

<br/>

After getting the `sample_data` dictionary, Use NuScenes devkit's `get_sample_data()` function to retrieve the data's absolute path. 

Then you may now load the image in any ways you'd like. Here's an example using `cv2`:
```
import cv2

data_path, boxes, camera_intrinsic = nusc.get_sample_data(sample_data_token)
img = cv2.imread(data_path)
cv2.imshow('fc_img', img)
cv2.waitKey()
```

Output: 
```
('{$dataset_root}/MARS_multitraversal/10/sweeps/CAM_FRONT_CENTER/1696454482897062.jpg',
[],
array([[661.094568 ,   0.       , 370.6625195],
       [  0.       , 657.7004865, 209.509716 ],
       [  0.       ,   0.       ,   1.       ]]))
```
![image](https://github.com/ai4ce/MARS/assets/105882130/e47b3fe4-fb98-4651-b3e8-0de360ea7d19)

---
### LiDAR Data
Same as loading camera data, we start with querying the `sample_data` dictionary for LiDAR sensor. 

Impoirt data calss "LidarPointCloud" from NuScenes devkit for convenient lidar pcd loading and manipulation.

The `.bcd.bin` LiDAR data in our dataset has 5 dimensions: [ x || y || z || intensity || ring ].

The 5-dimensional data array is in `pcd.points`. Below is an example of visualizing the pcd with Open3d interactive visualizer.


```
import open3d as o3d
from nuscenes.utils.data_classes import LidarPointCloud

sensor = 'LIDAR_FRONT_CENTER'
sample_data_token = my_sample['data'][sensor]
lidar_data = nusc.get('sample_data', sample_data_token)

data_path, boxes, _ = nusc.get_sample_data(my_sample['data'][sensor])

pcd = LidarPointCloud.from_file(data_path)
print(pcd.points)
pts = pcd.points[:3].T

# open3d visualizer
vis1 = o3d.visualization.Visualizer()
vis1.create_window(
    window_name='pcd viewer',
    width=256 * 4,
    height=256 * 4,
    left=480,
    top=270)
vis1.get_render_option().background_color = [0, 0, 0]
vis1.get_render_option().point_size = 1
vis1.get_render_option().show_coordinate_frame = True

o3d_pcd = o3d.geometry.PointCloud()
o3d_pcd.points = o3d.utility.Vector3dVector(pts)

vis1.add_geometry(o3d_pcd)
while True:
    vis1.update_geometry(o3d_pcd)
    vis1.poll_events()
    vis1.update_renderer()
    time.sleep(0.005)
```

Output: 
```
5-d lidar data: 
[[ 3.7755847e+00  5.0539265e+00  5.4277039e+00 ...  3.1050100e+00
   3.4012783e+00  3.7089713e+00]
 [-6.3800979e+00 -7.9569578e+00 -7.9752398e+00 ... -7.9960880e+00
  -7.9981585e+00 -8.0107889e+00]
 [-1.5409404e+00 -3.2752687e-01  5.7313687e-01 ...  5.5921113e-01
  -7.5427920e-01  6.6252775e-02]
 [ 9.0000000e+00  1.6000000e+01  1.4000000e+01 ...  1.1000000e+01
   1.8000000e+01  1.6000000e+01]
 [ 4.0000000e+00  5.3000000e+01  1.0200000e+02 ...  1.0500000e+02
   2.6000000e+01  7.5000000e+01]]
```

![image](https://github.com/ai4ce/MARS/assets/105882130/e28c8620-93e0-4a7a-890a-7a0f0635eeb4)


---
### IMU Data
IMU data in our dataset is saved as json files.
```
sensor = 'IMU_TOP'
sample_data_token = my_sample['data'][sensor]
lidar_data = nusc.get('sample_data', sample_data_token)

data_path, boxes, _ = nusc.get_sample_data(my_sample['data'][sensor])

imu_data = json.load(open(data_path))
print(imu_data)
```

Output:
```
{'utime': 1696454482879084,
'lat': 42.28098291158676,
'lon': -83.74725341796875,
'elev': 259.40500593185425,
'vel': [0.19750464521348476, -4.99952995654127e-27, -0.00017731071625348704],
'avel': [-0.0007668623868539726, -0.0006575787383553688, 0.0007131154834496556],
'acc': [-0.28270150907337666, -0.03748669268679805, 9.785771369934082]}
```
- `lat`: GPS latitude.
- `lon`: GPS longitude.
- `elev`: GPS elevation.
- `vel`: vehicle instant velocity [x, y, z] in m/s.
- `avel`: vehicle instant angular velocity [x, y, z] in rad/s.
- `acc`: vehicle instant acceleration [x, y, z] in m/s^2.

---
### Vehicle and Sensor Pose
Poses are represented as one rotation matrix and one translation matrix.
- rotation: quaternion [w, x, y, z]
- translation: [x, y, z] in meters

Sensor-to-vehicle poses may differ for different vehicles. But for each vehicle, its sensor poses should remain unchanged across all scenes & samples.

Vehicle ego pose can be quaried from sensor data. It should be the same for all sensors in the same sample.

```
# get the vehicle ego pose at the time of this FC_data
vehicle_pose_fc = nusc.get('ego_pose', FC_data['ego_pose_token'])
print("vehicle pose: \n", vehicle_pose_fc, "\n")

# get the vehicle ego pose at the time of this lidar_data, should be the same as that queried from FC_data as they are from the same sample.
vehicle_pose = nusc.get('ego_pose', lidar_data['ego_pose_token'])
print("vehicle pose: \n", vehicle_pose, "\n")

# get camera pose relative to vehicle at the time of this sample
fc_pose = nusc.get('calibrated_sensor', FC_data['calibrated_sensor_token'])
print("CAM_FRONT_CENTER pose: \n", fc_pose, "\n")

# get lidar pose relative to vehicle at the time of this sample
lidar_pose = nusc.get('calibrated_sensor', lidar_data['calibrated_sensor_token'])
print("CAM_FRONT_CENTER pose: \n", lidar_pose)
```

Output: 
```
vehicle pose: 
 {'token': 'q9e0pgk3wiot983g4ha8178zrnr37m50',
'timestamp': 1696454482883182,
'rotation': [-0.7174290249840286, 0.0, -0.0, -0.6966316057361065],
'translation': [-146.83352790433003, -21.327001411798392, 0.0]} 

vehicle pose: 
 {'token': '13y90okaf208cqqy1v54z87cpv88k2qy',
'timestamp': 1696454482883182,
'rotation': [-0.7174290249840286, 0.0, -0.0, -0.6966316057361065],
'translation': [-146.83352790433003, -21.327001411798392, 0.0]} 

CAM_FRONT_CENTER pose: 
 {'token': 'r5491t78vlex3qii8gyh3vjp0avkrj47',
'sensor_token': '1gk062vf442xsn86xo152qw92596k8b9',
'translation': [2.24715, 0.0, 1.4725],
'rotation': [0.49834929780875276, -0.4844970241435727, 0.5050790448056688, -0.5116695901338464],
'camera_intrinsic': [[661.094568, 0.0, 370.6625195], [0.0, 657.7004865, 209.509716], [0.0, 0.0, 1.0]],
'distortion_coefficient': [0.122235, -1.055498, 2.795589, -2.639154]} 

CAM_FRONT_CENTER pose: 
 {'token': '6f367iy1b5c97e8gu614n63jg1f5os19',
'sensor_token': 'myfmnd47g91ijn0a7481eymfk253iwy9',
'translation': [2.12778, 0.0, 1.57],
'rotation': [0.9997984797097376, 0.009068089160690487, 0.006271772522201215, -0.016776012592418482]}

```

<br/>

## LiDAR-Image projection
- Use NuScenes devkit's `render_pointcloud_in_image()` method.
- The first variable is a sample token.
- Use `camera_channel` to specify the camera name you'd like to project the poiint cloud onto.
```
nusc.render_pointcloud_in_image(my_sample['token'],
                                pointsensor_channel='LIDAR_FRONT_CENTER',
                                camera_channel='CAM_FRONT_CENTER',
                                render_intensity=False,
                                show_lidarseg=False)
```

Output: 

![image](https://github.com/ai4ce/MARS/assets/105882130/f50623e1-fa79-4e59-9daf-b76a760d20f5)







