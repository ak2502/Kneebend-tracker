import cv2
import mediapipe as mp
import numpy as np
import time
mp_drawing = mp.solutions.drawing_utils  # Drawing utility
mp_pose = mp.solutions.pose  # Pose estimation model

def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    angle = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(angle*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

cap = cv2.VideoCapture("KneeBend.mp4")

activate_video_record=0
counter = 0
status = "down"
exercise_status = ""
original_image = None

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        original_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        image = np.multiply(image, image < 180)

        results = pose.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        try:
            landmarks = results.pose_landmarks.landmark

            left_hip = mp_pose.PoseLandmark.LEFT_HIP.value
            left_knee = mp_pose.PoseLandmark.LEFT_KNEE.value
            left_ankle = mp_pose.PoseLandmark.LEFT_ANKLE.value

            left_hip = [landmarks[left_hip].x , landmarks[left_hip].y]
            left_knee = [landmarks[left_knee].x, landmarks[left_knee].y, landmarks[left_knee].z]
            left_ankle = [landmarks[left_ankle].x, landmarks[left_ankle].y]

            right_hip = mp_pose.PoseLandmark.RIGHT_HIP.value
            right_knee = mp_pose.PoseLandmark.RIGHT_KNEE.value
            right_ankle = mp_pose.PoseLandmark.RIGHT_ANKLE.value

            right_hip = [landmarks[right_hip].x , landmarks[right_hip].y]
            right_knee = [landmarks[right_knee].x, landmarks[right_knee].y, landmarks[right_knee].z]
            right_ankle = [landmarks[right_ankle].x, landmarks[right_ankle].y]

            #considering leg closer to camera as exercise leg
            if left_knee[2] - right_knee[2] > 0:
                hip = right_hip
                knee = right_knee
                ankle = right_ankle

            else:
                hip = left_hip
                knee = left_knee
                ankle = left_ankle

            angle = calculate_angle(hip, knee, ankle)

            # counting reps, feedback logic
            if angle > 157:
                if status == "up":
                    end = time.time()
                    if end - start >= 8:    #holding timer
                        counter += 1
                        exercise_status = ""
                    else:   #feedback message
                        exercise_status = "Keep your knee bent"
                status = "down"
                
            if angle <= 157 and status == "down":
                start = time.time()
                status = "up"
                exercise_status = ""


        except:
            pass

        image = original_image
        
        cv2.putText(image, exercise_status, (300,60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(image, 'REPS:'+str(counter), (70,40), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2,cv2.LINE_AA)
        cv2.putText(image, 'Status:'+status.upper(),(70,80), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0, 0), 2, cv2.LINE_AA)
        
        mp_drawing.draw_landmarks(image, results.pose_landmarks,mp_pose.POSE_CONNECTIONS)
        
        cv2.imshow('Output Video', image)
        if cv2.waitKey(10) == ord('q'):
            break

        if  activate_video_record == 0:
            out = cv2.VideoWriter('Output Video.avi',cv2.VideoWriter_fourcc(*'DIVX'), 20, (640,480))
            activate_video_record = 1

        out.write(image)

    cap.release()
    cv2.destroyAllWindows()
