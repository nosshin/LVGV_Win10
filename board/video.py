import cv2
import numpy as np
import tensorflow as tf
from flask import Response, Blueprint
from flask_restx import Namespace, Resource, Api  # Api를 추가로 import합니다.

bp_video = Blueprint("video", __name__)

# 모델 로드 (모델 경로를 적절히 수정하세요)
model_path = './models/my_model.keras'
model = tf.keras.models.load_model(model_path)
class_labels = ['bottle', 'brick', 'gun', 'knife']
threshold = 0.6  # 임계값 설정

# Flask-RestX Namespace 생성
video_ns = Namespace('video', description='Video operations')

@video_ns.route('/video_feed')
class VideoFeed(Resource):
    @video_ns.doc(responses={200: 'OK', 400: 'Invalid Argument'})
    def get(self):
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def generate_frames(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Error: Could not open webcam.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 프레임 전처리
            img_size = (224, 224)
            frame_resized = cv2.resize(frame, img_size)
            frame_normalized = frame_resized / 255.0
            frame_expanded = np.expand_dims(frame_normalized, axis=0)

            # 모델 예측
            preds = model.predict(frame_expanded)
            pred_prob = np.max(preds)
            pred_label = np.argmax(preds, axis=1)[0]

            # 임계값 확인 및 클래스 결정
            if pred_prob < threshold:
                pred_class = "No_class"
            else:
                pred_class = class_labels[pred_label]

            # 예측된 클래스 확인
            cv2.putText(frame, f'Prediction: {pred_class}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # 프레임 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cap.release()

# Flask-RestX Namespace를 Blueprint에 등록
api = Api(bp_video, version='1.0', title='Video API', description='APIs for Video operations')
api.add_namespace(video_ns)
