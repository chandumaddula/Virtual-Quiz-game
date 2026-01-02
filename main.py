import cv2
import csv
from cvzone.HandTrackingModule import HandDetector
import cvzone
import time


cap = cv2.VideoCapture(0) # webcam setup
cap.set(3,1280)
cap.set(4,500)
detector = HandDetector(detectionCon=0.8)    # mimimum detection confidence 0.8


class mcq():
    def __init__(self, data):               # data is a list of question and options
        self.Question = data[0] 
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])

        self.userAns = None        #default user answer
        self.isAnswered = False    #default is answered or not

    def update(self, cursor, bboxs):
        for i, bbox in enumerate(bboxs):    # iterate through each bounding box
            x, y, w, h = bbox               # unpack the bounding box
            if x < cursor[0] < w and y < cursor[1] < h:

                self.userAns = i+ 1         # update user answer (i+1 because index starts from 0)

                cv2.rectangle(img, (x,y), (w,h), (0, 255, 0), cv2.FILLED)   # highlight the selected option
                self.isAnswered = True      # mark as answered
            



pathcsv = 'mcq.csv'                   # importing the  csv file    
with open(pathcsv,newline='\n') as f: #
    reader = csv.reader(f)              
    data_all = list(reader)[1:]       # Skip the header line
    data_all = [row for row in data_all if len(row) == 6]   # Keep only rows with exactly 6 elements



# creating list of mcq objects
mcqlist = []          # list to hold mcq objects

for q in data_all:    # iterate through each row in the csv
    if len(q) < 6:    # 
        continue      # skip empty or broken rows
    mcqlist.append(mcq(q))

print(len(mcqlist))   # print number of questions loaded

Qno = 0                   # current question number
Qtotal = len(data_all)     # total number of questions
#print(data)


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    if Qno < Qtotal:        # if there are still questions left
        mcq = mcqlist[Qno]      # get the current mcq object


        img, bbox = cvzone.putTextRect(img, mcq.Question, [100, 100], 2, 2, offset=50, border=5)    # offset and border for better visibility 
        img, bbox1 = cvzone.putTextRect(img, mcq.choice1, [100, 250], 2, 2, offset=30, border=5)    
        img, bbox2 = cvzone.putTextRect(img, mcq.choice2, [400, 250], 2, 2, offset=30, border=5)    
        img, bbox3 = cvzone.putTextRect(img, mcq.choice3, [100, 400], 2, 2, offset=30, border=5)    
        img, bbox4 = cvzone.putTextRect(img, mcq.choice4, [400, 400], 2, 2, offset=30, border=5)

        #hands, img = detector.findHands(img)

        if hands:                    # if hands are detected
            hand = hands[0]          # get the first hand
            lmList = hand['lmList']  # list of 21 Landmark points

            x1, y1, _ = lmList[8]   # tip of index finger
            x2, y2, _ = lmList[12]  # tip of middle finger
            length, info, _ = detector.findDistance((x1, y1), (x2, y2))
            
            if length < 30:    # if distance between index and middle finger is less than 70 pixels
            #print("Click")
                mcq.update(cursor=(x1, y1), bboxs=[bbox1, bbox2, bbox3, bbox4])
                print(mcq.userAns)
                if mcq.userAns != None:
                    time.sleep(0.3)    # to avoid multiple detection of answers
                    Qno += 1
    else:
        score = 0
        for mcq in mcqlist:
            if mcq.userAns == mcq.answer:
                score += 1
        score = round((score/Qtotal)*100, 2)    

        #img = cv2.imread("score.png")
        img, _ = cvzone.putTextRect(img, 'Quiz is completed', [250, 300], 2,2,(255,0,0),offset=16)
        img,_ = cvzone.putTextRect(img, f'Your Score: {score}%', [700,300 ],2, 2,(255,0,0), offset=16)
        img,_ = cvzone.putTextRect(img, f'congratulations !', [500,500 ],2, 2,(255,0,0),offset=16)
        #img, _ = cvzone.putTextRect(img, f'Your Score: {score} %', [250, 400], 2,2, offset=50, border=5)

    # display the progress

    barValue = 150 + (950 // Qtotal) * Qno
    cv2.rectangle(img,(150,600),(barValue,650),(255,255,0),cv2.FILLED)
    cv2.rectangle(img,(150,600),(1100,650),(255,0,0),5)

    img,_ = cvzone.putTextRect(img, f'{round((Qno/ Qtotal)*100)}%', [1130,635 ],2, 2, offset=16)
    cv2.imshow("Answer the questions: ", img)
    if cv2.waitKey(1) & 0xFF == ord('c'):       # press c to quit
        break

cv2.waitKey(1)           
cv2.destroyAllWindows()
 