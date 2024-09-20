from ultralytics import YOLO

model = YOLO('yolov5nu.pt')


results = model.train(
    data='/Users/nijatkaazimli/Desktop/training/data.yml',
    epochs=50,
    imgsz=640,
    batch=16,
    name='yolov5-custom',
    device='cpu', # try if other options like gpu or mps (macbook silicion cpus) are faster
)


# To resume
# model = YOLO('/Users/nijatkaazimli/Desktop/training/runs/detect/yolov5-custom/weights/last.pt')
# a path to the last model.


# results = model.train(
#     data='/Users/nijatkaazimli/Desktop/training/data.yml',
#     epochs=50,
#     imgsz=640,
#     batch=16,
#     name='yolov5-custom',
#     device='cpu', # try if other options like gpu or mps (macbook silicion cpus) are faster
#     resume=True # Important
# )
