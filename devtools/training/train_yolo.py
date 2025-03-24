from ultralytics import YOLO

model = YOLO("yolo11l-cls.pt")

results = model.train(data="data/set_2/split", cfg="devtools/args.yaml", plots=True)
