from ultralytics import YOLO 

# YOLO pretrained model 
model = YOLO('yolov8n.pt')

save_path = 'Models'
n_epochs = 30

# requires full path (not relative path)
dataset_path = ""
train_res = model.train(data=dataset_path,
                        save_dir=save_path,
                        epochs=n_epochs)