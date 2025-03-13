from ultralytics import YOLO
import os

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

model = YOLO("yolo11l-cls.pt")

results = model.train(data="data/set_1/split", cfg="devtools/args.yaml", plots=True)