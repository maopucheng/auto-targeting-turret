from cvzone.HandTrackingModule import HandDetector
import cv2
import cvzone

fpsReader = cvzone.FPS()
cap = cv2.VideoCapture(0)

detector = HandDetector()

while True:
    # Get image frame
    success, img = cap.read()
    # img = cv2.flip(img, 180)

    fps, img = fpsReader.update(
        img, pos=(50, 80), color=(0, 255, 0), scale=3, thickness=5
    )

    # Find the hand and its landmarks
    hands, img = detector.findHands(img)  # with draw
    # hands = detector.findHands(img, draw=False)  # without draw

    if hands:
        # Hand 1
        hand1 = hands[0]
        lmList1 = hand1["lmList"]  # List of 21 Landmark points
        bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
        centerPoint1 = hand1['center']  # center of the hand cx,cy
        handType1 = hand1["type"]  # Handtype Left or Right

        fingers1 = detector.fingersUp(hand1)
        # print(fingers1)
        if fingers1[1:5] == [0, 1, 0, 0]:  # 大拇指不在里面
            print("不许说脏话！")
        elif fingers1[1:5] == [1, 1, 0, 0]:
            print("你赢了！")
        elif fingers1 == [1, 1, 1, 1, 1]:
            print("我出包子！")

        #     # Find Distance between two Landmarks. Could be same hand or different hands
        #     length, info, img = detector.findDistance(
        #         lmList1[8], lmList2[8], img
        #     )  # with draw
        #     # length, info = detector.findDistance(lmList1[8], lmList2[8])  # with draw

    # Display
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
