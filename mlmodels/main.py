import cv2
import time
import numpy as np
import mediapipe as mp
import onnxruntime as ort
import os

from parentClass.main import DMSLMMain
import threading


def detect_eyes(image):
    h, w, _ = image.shape
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.multi_face_landmarks:
            return None, None, None, None

        landmarks = results.multi_face_landmarks[0]

        # Mesh IDs for each eye region
        left_ids = [33, 133, 160, 159, 158, 153]
        right_ids = [362, 263, 387, 386, 385, 380]

        def extract_bbox(ids):
            xs = [int(landmarks.landmark[i].x * w) for i in ids]
            ys = [int(landmarks.landmark[i].y * h) for i in ids]
            x1, x2 = min(xs) - 5, max(xs) + 5
            y1, y2 = min(ys) - 5, max(ys) + 5
            return (x1, y1, x2, y2)

        left_bbox = extract_bbox(left_ids)
        right_bbox = extract_bbox(right_ids)

        left_eye = image[left_bbox[1]:left_bbox[3], left_bbox[0]:left_bbox[2]]
        right_eye = image[right_bbox[1]:right_bbox[3], right_bbox[0]:right_bbox[2]]

        return left_eye, right_eye, left_bbox, right_bbox


class dMonitoring(DMSLMMain):
    """
    Driver Monitoring System Eye Detector
    Tracks eyes with bounding-box updates every frame, only ONNX inference on eye patches.
    """

    def __init__(self,main, model_path="ocec_p.onnx"):
        self.main=main
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        # store bounding boxes
        self.last_updated = 0
        self.update_rate = 1.0 / 8.0
        self.bbox = {"left": None, "right": None}
        threading.Thread(target=self.continuscheck, daemon=True).start()


    def preprocess(self, img):
        img = cv2.resize(img, (40, 24))
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = img[np.newaxis, :, :, :]
        return img
    

    def predict_eye(self, img):
        img = self.preprocess(img)
        output = self.session.run(None, {self.input_name: img})[0]
        prob = float(output)
        return "open" if prob > 0.5 else "closed"

    def update_bbox(self, frame):
        import time
        now=time.time()
        if now - self.last_updated < self.update_rate :
            return
        
        

        self.last_updated = now


        left_eye, right_eye, left_bbox, right_bbox = detect_eyes(frame)
        if left_eye is None or right_eye is None:
            return

        def need_update(old, new):
            if old is None:
                return True
            return (abs(old[0] - new[0]) > 2 or abs(old[1] - new[1]) > 2)

        if need_update(self.bbox['left'], left_bbox):
            self.bbox['left'] = left_bbox

        if need_update(self.bbox['right'], right_bbox):
            self.bbox['right'] = right_bbox

    def crop_from_bbox(self, frame, bbox):
        x1, y1, x2, y2 = bbox
        return frame[y1:y2, x1:x2]

    def check(self, frame):
        if self.bbox['left'] is None or self.bbox['right'] is None:
            return {"error": "bbox not initialized"}

        left_crop = self.crop_from_bbox(frame, self.bbox['left'])
        right_crop = self.crop_from_bbox(frame, self.bbox['right'])

        left_state = self.predict_eye(left_crop)
        right_state = self.predict_eye(right_crop)


        #producer.push( "time": time.time(),
         #   "left_eye": left_state,
        #    "right_eye": right_state
         #)

        return {
            "time": time.time(),
            "left_eye": left_state,
            "right_eye": right_state
        }
    def continuscheck(self):
        import numpy as np, cv2
        while True:
            try:
                item = self.main.imageQueue.get()   # FIXED: no tuple unpack
                #print("Fetched data from queue:", item["time"])
                jpg = np.frombuffer(item["bytes"], dtype=np.uint8)
                frame = cv2.imdecode(jpg, cv2.IMREAD_COLOR)
                if frame is None:
                    print("❌ Failed to decode frame, skipping")
                    continue
                
                self.update_bbox(frame)
                result = self.check(frame)
                result["time"] = item["time"]
                #print(result,time.time())
                self.main.processdImageJsonQueue.put(result)
                #print("end",time.time(),"ms")
                #print("Added to processedImageJsonQueue")
            except Exception as e:
                print("🔥 Error in continuscheck:", e)
                continue


