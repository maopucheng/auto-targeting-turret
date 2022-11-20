from cvzone.FaceDetectionModule import FaceDetector
import cv2
import cvzone

fpsReader = cvzone.FPS()
cap = cv2.VideoCapture(0)
detector = FaceDetector()

while True:
    success, img = cap.read()
    fps, img = fpsReader.update(
        img, pos=(50, 80), color=(0, 255, 0), scale=5, thickness=5
    )
    img, bboxs = detector.findFaces(img)

    if bboxs:
        # bboxInfo - "id","bbox","score","center"
        center = bboxs[0]["center"]
        center = (10, 10)
        cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
