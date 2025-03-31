from pathlib import Path

from ultralytics import YOLO

model = YOLO("../runs/classify/train2/weights/best.pt")

test_dir = Path("data/set_3/split/test")

correct = 0
total = 0
for img in (test_dir / "defective").glob("*.jpg"):
    result = model.predict(img, verbose=False)[0]
    result = result.probs.top1 == 0
    if result:
        correct += 1
    total += 1
print(f"Defective: {correct} correct out of {total} total")

correct = 0
total = 0
for img in (test_dir / "non-defective").glob("*.jpg"):
    result = model.predict(img, verbose=False)[0]
    result = result.probs.top1 == 1
    if result:
        correct += 1
    total += 1
print(f"Non defective: {correct} correct out of {total} total")
