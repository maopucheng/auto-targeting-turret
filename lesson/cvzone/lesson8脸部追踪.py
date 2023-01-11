from cvzone.FaceDetectionModule import FaceDetector
import cv2
import cvzone

fpsReader = cvzone.FPS()
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

detector = FaceDetector()
success, img = cap.read()
print(img.shape)
while True:
    success, img = cap.read()
    fps, img = fpsReader.update(
        img, pos=(50, 80), color=(0, 255, 0), scale=5, thickness=5
    )
    img, bboxs = detector.findFaces(img)

    if bboxs:
        # bboxInfo - "id","bbox","score","center"
        center = bboxs[0]["center"]
        cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
