from ultralytics import YOLO

model = YOLO('yolo11n.pt') 

if __name__ == '__main__':
    model.train(
        data='data.yaml',
        epochs=50,
        imgsz=640,
        device='cpu' # خليه CPU بما إننا نتدرب لوكال
    )