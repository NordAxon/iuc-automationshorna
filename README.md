# IUC Syd jar defect detector

 This project is NordAxon's contribution to IUC Syd's automationshörna (automation corner) at Tobaksfabriken in Malmö. The automation corner is a demo of industrial automation techniques created by members and collaborators of IUC Syd.

 The solution consists of a computer vision model running on an Nvidia Jetson Orin Nano Super, detecting defects in black plastic jars running by on a conveyor belt. The model is a binary classifier, classifying every jar as defective or non-defective. 

 This project was created by Petter at NordAxon during the spring of 2025.

## How it works

INCLUDE PICTURES OF THE CONVEYOR BELT WITH CAMERA, AND OF THE JARS (BOTH DEFECTIVE AND NORMAL) ON THE CONVEYOR BELT, FROM THE CAMERA'S PERSPECTIVE.

At the time of writing, the setup works like this: jars travel along a conveyor belt until they pass in front of an optical proximity sensor. The sensor then sends a signal to Intelligent Bridge's gateway, letting the gateway know there is a jar at the sensor's position. In response, the gateway stops the conveyor belt. Simultaneously, our program is alerted by the gateway that a jar is present and our camera, located by the sensor, captures a picture of the jar. The image of the jar is fed into an image classifier that determines if the jar is defective or not. The class of the jar is sent back to the gateway which can then act on the information, for example by instructing a robot arm to pick up and dispose of the jar if it is defective. After acting on the information from the classifier, the gateway restarts the conveyor belt, and the cycle repeats. It should be noted that the setup is modular and modifiable and may have changed by the time you are reading this.

A diagram of the complete system is shown below, with this project's contributions outlined in green. 

![A block diagram showing the different components of the system and how they communicate and coordinate](images/conveyor.drawio.svg)

### Physical deployment

The solution is deployed on an Nvidia Jetson Orin Nano Super attached to the undercarriage of the conveyor belt. The camera is a cheap USB camera (HP Poly Studio P5), mounted to the side of  the conveyor belt and connected to the Jetson. To capture vertical images (to match the training data and aspect ratio of the jars), the camera was attached sideways and the images were rotated before being fed into the model. Attachment of both the Jetson and the camera was handled by Leo, our contact at IUC Syd, who 3D printed attachment solutions. The Jetson is connected via ethernet to a local network shared with Intelligent Bridge's gateway. 

### Communication with Intelligent Bridge's gateway

The communication with Intelligent Bridge's gateway is done over MQTT, a messaging protocol for IoT and edge. The gateway acts as an MQTT broker that the Jetson connects to. Every time the proximity sensor senses something, ```1``` is published to the topic ```iuc/robotdemo/conveyorSensor```. The application is subscribed to this topic, and recieving a ```1``` on it trigges the image capture and inference. When inference has been completed, the result is published to the topic ```iuc/robotdemo/defectJar```. If the jar is deemed defective, ```1``` is published, otherwise ```0```.

### Implementation

The model training and inference was done using the ultralytics python package, using their implementation of Yolo11 (large). For handling MQTT communication, the python package paho-mqtt was used. 

To capture images from the camera, OpenCV was used. OpenCV cannot easily capture single images from USB webcams, only video streams. To perform image capture with low latency, a video capture stream is kept running and a background thread continually empties the stream buffer so the latest frame is available to the application with minimal latency.

#### Training

HA MED TRAINING CONFIG YAML! OCH NÄMN KANSKE BILDUPPLÖSNING?

Since the application is just a demo, we had the opportunity to choose what kind of defects to identify. For ease of collection training data, and because we only had access to six jars, it was decided that the defects would be discolorations on the sides of the jars.

Because we did not have access to the production line and USB camera when the training data was collected, and because we did not know exactly where the camera would be located in relation to the jars, efforts were taken to collect diverse but realistic training data that would enable the model to recognize defective jars in any photo. Therefore, images of jars were taken against different backgrounds, in different lighting, and from different distances and angles. The training images were captured using Petter's phone, in an 16:9 aspect ratio (vertical). 

To collect training data of defective jars, spots, lines, drawings, squiggles, etc. were drawn on the jars with different coloured markers. To collect training data of non-defective jars, similar photos were taken of normal jars. In total, ~250 images of defective jars and ~200 of non-defective jars were taken. They can be found in NordAxon's OneDrive under ```PROJECTS/IUC Syd/data```.  

#### Deployment

The application is deployed on the Jetson using the systemd service ```jar_defect_detector.service```. It runs the script ```run_app.sh```. Important parameters are specified in a .env file, an example of which can be seen in the section "Running the app" of this README. 

## Installation

This project has been developed using uv as package manager. The easiest way to get it running is to use uv. It has been developed for the Nvidia Orin Nano Super using JetPack 6.2, CUDA 12.6, and Python 3.10. No guarantees are made that it will work on other setups, but it should not be a problem if you have some experience managing Python environments.

### Installing on Jetson

The following instructions are specific to JetPack 6.2, CUDA 12.6, and Python 3.10. 

Begin by creating a python venv using uv:
```
uv sync
```
Now you need to install PyTorch with support for the Jetson's iGPU. The regular torch version that uv installs by default will not be able to use the iGPU.

First, some prerequesites need to be installed:
```
sudo apt-get -y update;

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/arm64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get -y install python3-pip libcusparselt0 libcusparselt-dev  libopenblas-dev
```

Now, install the JetPack specific python wheels for torch and torchvision provided by Nvidia:
```
uv pip install https://pypi.jetson-ai-lab.dev/jp6/cu126/+f/6cc/6ecfe8a5994fd/torch-2.6.0-cp310-cp310-linux_aarch64.whl
uv pip install https://pypi.jetson-ai-lab.dev/jp6/cu126/+f/aa2/2da8dcf4c4c8d/torchvision-0.21.0-cp310-cp310-linux_aarch64.whl
```
These are specific torch & torchvision releases, built by Nvidia for JetPack 6 with CUDA 12.6. If other releases or additional packages are desired, they can be found [here](https://pypi.jetson-ai-lab.dev/). Simply replace the urls in the commands above with urls to other wheels. 

Finally, we can install the project itself:
```
uv pip install -e .
```

Optional: JetPack comes with many python packages built specifically for JetPack preinstalled. None of them are required for this project, but they could be useful for further development (for example, deploying the model using TensorRT). To make use of them in the venv without having to manually install them, create a venv that includes system site packages:
```
uv venv --system-site-packages
```
This must be run before running uv sync.

Final note: There exists a version of opencv compiled specifically for JetPack, but it does not seem to be necessary. The version you get with uv seems to work fine. Same actually goes for torchvision, but we added that to the installation instructions in case it provides a speed up or something.

### Installing on a regular computer
```
uv sync
uv pip install -e .
```
GPU support may or may not be included. We had issues on Windows but not on WSL. Figure it out yourself.

## Running the app

Before you can run the app, you need to create an env file. Create a file called .env in the project root. Here is an example file that contains all the necessary fields:

```
# MQTT stuff
BROKER_IP=localhost
BROKER_PORT=1883
CONNECT_TIMEOUT=30
JAR_SENSOR_TOPIC=iuc/robotdemo/conveyorSensor
DEFECT_TOPIC=iuc/robotdemo/defectJar

# Logging
LOG_LEVEL=DEBUG

# Inference config
MODEL_PATH=../weights/best.pt
INFERENCE_DEVICE=cuda

# Camera config
IMAGE_HEIGHT=480
IMAGE_WIDTH=480
# 0 for 90 degrees, 1 for 180, 2 for 270.
IMAGE_ROTATION=2
IMAGE_SOURCE=0
GET_IMAGE_TIMEOUT=0.5
```

After that, you can run the app by running main.py using your virtual environment, or, assuming you installed with uv, you can run ```bash run_app.sh```. 

## Testing

To facilitate end to end testing without having access to the actual production line, the script ```mqtt_testing/end-to-end-test.sh``` was created. This script: 
- starts an mqtt broker running in a docker container on localhost
- starts a python script that connects to the broker and publishes ```1``` on the jar sensor topic every three seconds
- starts a python script that connects to the broker and prints the contents of every message received on the jar defect topic
- starts the main app, connecting to the broker
- on Ctrl + C, all scripts and the container are shut down

For debugging, all the components of the test can be run manually and debugged like usual. 

## Issues encountered & their solutions

Here are some of the issues encountered during development and their solutions, documented for posterity. 

* The most recent version of Docker did not work on JetPack 6.2. Something about the iptable 'raw' not existing. Nvidia's suggested solution was to recompile the kernel, but we opted to downgrade to docker 27.3.0 instead. Works just fine. 

* The webcam used does not have Linux drivers. It can take images, but we could not seem to capture images in higher resolution than 640x480. This was not a problem since the model was not trained at high resolution, but could be worth keeping in mind for further development.

* Taking pictures with a usb webcam from python was more complicated than expected. We could not find any convenient way to take a single photo from within python. Rather, a video stream had to be started, and a frame grabbed from that stream. However, opening a stream every time an image is to be taken introduces significant latency, as the video stream takes ~0.5 seconds to start (likely because the camera has to wake up). To solve this, a single video stream was kept running at all times. OpenCV's VideoCapture captures all frames and places them on a buffer, from which the frames have to be retrieved in the order they were captured. To avoid the buffer growing unreasonably large, and to make the newest frame is always retrieved, a thread was set up to continually retrieve and discard frames from the buffer. When an image is to be captured, the next frame to be placed on the buffer will be returned, ensuring low latency. A little inefficient, but it works.

* Flashing JetPack 6.2 to the Jetson from Marvin (our training computer running Ubuntu 22.04) took some time because of cryptic errors. The problem was that Ubuntu's ufw (uncomplicated firewall) was blocking the connection to the Jetson. To solve this problem, the ufw was temporarily disabled while flashing. 

* We tried doing inference using ONNX and TensorRT, using the built in functions for this in ultralytics. However, we got errors indicating some tensors were of the wrong shape. Solution: stick to PyTorch. 

* Single bits cannot be sent over MQTT. The minimum message size is one byte. Solution: send ASCII representations of ```0``` or ```1``` instead. This can be accomplished in python by sending the byte string ```b'0'``` or ```b'1'```. 

* Running an inference every few seconds is not intensive enough for the Jetson's iGPU to clock up, increasing inference time. If low latency is desired, the Jetson can be forced to maintain max clocks at all times by running ```sudo jetson_clocks```. For this initial deployment, this was deemed unnecessary as the inference was fast enough anyway.