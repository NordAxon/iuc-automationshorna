from ultralytics import YOLO

model = YOLO("yolo11l-cls.pt")

results = model.train(data="data/set_3/split", cfg="devtools/training/args.yaml", plots=True)
