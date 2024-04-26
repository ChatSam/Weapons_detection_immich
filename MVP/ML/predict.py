from ultralytics import YOLO
from PIL import Image
import cv2
from io import BytesIO

class ThreatDetector:
    def __init__(self, model_path=None):
        if model_path:
            self.initialize_model(model_path)


    def run_prediction_image(self, image, confidence=0.15):
        #model(source=1, show=True, conf=0.4, save=True)
        prediction_result = self.model(image, conf=confidence)
        return prediction_result 
    

    def run_prediction_bitstream(self, byte_image, save_path=None):
        reconstructed_image = Image.open(byte_image)
        prediction_result = self.run_prediction_image(reconstructed_image)[0]

        if save_path:
            self.save_detections_image(prediction_result, save_path)
            print (f"Detection saved at {save_path}")

        return prediction_result


    def save_detections_image(self, detected_result, save_path):
        """ Saves the thumbnails of detection
        """
        detected_result.plot(save=True, filename=save_path)
         

    def initialize_model(self, model_path):
        self.model = YOLO(model_path)


    def run_prediction_video(self, video_path, output_path, confidence=0.2):
        video_cap = cv2.VideoCapture(str(video_path))
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        frame_size = (int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        fourcc = cv2.VideoWriter_fourcc(*'X264')
        out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

        ret = True 

        while ret:
            ret, frame = video_cap.read()

            if ret:
                results = self.model.track(frame, persist=True, conf=confidence)

                frame_ = results[0].plot()

                out.write(frame_)  # Write the frame into the file 'output.avi'

        video_cap.release()
        out.release()  # Release the VideoWriter



if __name__ == '__main__':
    model_path = '/Users/chatsam/P_Dev/Weapons_detection_immich/MVP/ML/Models/train9_model_v1.pt'
    test_image_path = '/Users/chatsam/P_Dev/Weapons_detection_immich/MVP/ML/Test/test_weapon.jpg'
    detected_img_save_path = '/Users/chatsam/P_Dev/Weapons_detection_immich/MVP/ML/Test/detection.jpg'

    test_image = Image.open(test_image_path)
    byte_image = BytesIO()
    test_image.save(byte_image, format="jpeg")

    threat_detector = ThreatDetector(model_path)

    reconstructed_image = Image.open(byte_image)
    detection_result = threat_detector.run_prediction_image(reconstructed_image)[0]

    # save the detected result
    detection_result.plot(save=True, filename=detected_img_save_path)

    print (detection_result[0])
