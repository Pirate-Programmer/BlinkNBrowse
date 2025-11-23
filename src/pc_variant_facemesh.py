import cv2 as cv
import mediapipe as mp
import math
import time


#global settings (change em to gain fps on raspberry pi)
camera_input = 1
width = 640
height = 480
fps = 20

#Eye settings (no not augments this aint cyberpunk)
left_eye_coords = [33, 160, 158, 133, 153, 144]
right_eye_coords = [362, 385, 387, 263, 373, 380]
EAR_threshold = 0.2
valid_blink_duration = 0.5

class FaceMesh():

    #intializing
    def __init__(self):
        #setup webcam for capturing live frames
        self.capture = cv.VideoCapture(camera_input)

        if not self.capture.isOpened():
            print("Err opening camera\nexiting...")
            exit(1)



        # self.capture.set(cv.CAP_PROP_FRAME_WIDTH,width)
        # self.capture.set(cv.CAP_PROP_FRAME_HEIGHT,height)
        # self.capture.set(cv.CAP_PROP_FPS,fps)

        print(f"width: {self.capture.get(cv.CAP_PROP_FRAME_WIDTH)} height: {self.capture.get(cv.CAP_PROP_FRAME_HEIGHT)}")

        #load facemesh module and landmark drawing modules
        self.mp_face_mesh = mp.solutions.face_mesh 
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        #init facemesh model 
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces = 10,                #no of faces to be detected in frame
            refine_landmarks = True,         #better landmark details but cpu intensive 
            min_detection_confidence = 0.5,  #threshold for face detection
            min_tracking_confidence = 0.5,   #tracking across frames
        )

        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        
        self.left_eye_flag = False
        self.left_eye_time = 0

        self.right_eye_flag = False
        self.right_eye_time = 0
    

    def startCapture(self):
        print("Press 'Q' to quit/exit")
        while True: 
            isFrame,frame = self.capture.read()
            
            #check to see frame has been read
            if isFrame:
                frame.flags.writeable = False
                frame_rgb = cv.cvtColor(frame,cv.COLOR_BGR2RGB)
                result = self.face_mesh.process(frame_rgb)
                
                if result.multi_face_landmarks:
                    h,w,_ = frame.shape
                    self.getEyeLandmarks(result,h,w)
                    self.calc_EAR()
            


            
                    frame.flags.writeable = True

                   # print(self.EAR[0],self.EAR[1])

                    #left eye is shut
                    if self.EAR[0] <= EAR_threshold:
                        if not self.left_eye_flag:
                            self.left_eye_flag = True
                            self.left_eye_time = time.time()
                    
                    if self.left_blink():
                        pass #Put some fuction

                    if self.right_blink():
                        pass #put some function



                    # if self.EAR[1] < EAR_threshold: 
                    #     self.left_eye_flag = True

                    # if self.EAR[0] < EAR_threshold:
                    #     self.right_eye_flag = True

                
                   # cv.putText(frame, f"Left Eye: {"Close" if self.EAR[1] < EAR_threshold else "Open"}",(w//2 - 300,h//2),cv.FONT_HERSHEY_COMPLEX,1.0, (0,255,0))
                    #cv.putText(frame, f"Left Eye: {"Close" if self.EAR[1] < EAR_threshold else "Open"}",(w//2 - 300,h//2),cv.FONT_HERSHEY_COMPLEX,1.0, (0,255,0))

                    #frame = cv.flip(frame,1)

                    #self.drawLandmarks(result,frame)
                    cv.imshow("landmarks", frame)

                
            #exit on key press Q
            if cv.waitKey(10) & 0xFF == ord('q'):
                print("exiting ...")
                break

        #release the videocapture
        self.capture.release()

        #welp what the name says
        cv.destroyAllWindows()



    def right_blink(self) -> bool:
        if self.EAR[0] <= EAR_threshold:
            if not self.right_eye_flag:
                self.right_eye_flag = True
                self.right_eye_time = time.time()
        
        #eye is open, check if previous it was closed
        elif self.right_eye_flag:
            self.right_eye_flag = False 
            if time.time() - self.right_eye_time >= valid_blink_duration:
                print("Right Eye blink")
                return True
        return False                

    
    def left_blink(self) -> bool:
        if self.EAR[1] <= EAR_threshold:
            if not self.left_eye_flag:
                self.left_eye_flag = True
                self.left_eye_time = time.time()
        
        #eye is open check if previous it was closed
        elif self.left_eye_flag:
            self.left_eye_flag = False 
            if time.time() - self.left_eye_time >= valid_blink_duration:
                print("Left Eye blink")
                return True
        return False


    def getEyeLandmarks(self,result,h,w):
        landmarks = result.multi_face_landmarks[0].landmark
        self.left_eye = [landmarks[i] for i in left_eye_coords]
        self.right_eye = [landmarks[i] for i in right_eye_coords]

        # #converting normalized to pixel coords (NOTE REMOVE THIS IF NOT USED LATER)
        # for i in range(6):
        #     self.left_eye[i].x, self.left_eye[i].y = int(self.left_eye[i].x * w),int(self.left_eye[i].y * h)
        #     self.right_eye[i].x, self.right_eye[i].y = int(self.right_eye[i].x * w),int(self.right_eye[i].y * h)


    #calculate EAR of left and right eye
    def calc_EAR(self):
        self.EAR = []
        for i in (self.left_eye,self.right_eye):
            p1,p2,p3,p4,p5,p6 = self._coords(i)
            ear = (math.dist(p2,p6) + math.dist(p3,p5)) / (2 * math.dist(p1,p4))
            self.EAR.append(ear)


    #helper function to extract coords from landmarks
    def _coords(self,landmarks):
        coords = []
        for i in landmarks:
            coords.append((i.x,i.y))
        return coords


    def drawLandmarks(self,result,image):
      image.flags.writeable=True
      for face_landmarks in result.multi_face_landmarks:
        # self.mp_drawing.draw_landmarks(
        #     image=image,
        #     landmark_list=face_landmarks,
        #     connections=self.mp_face_mesh.FACEMESH_TESSELATION,
        #     landmark_drawing_spec=None,
        #     connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style())
        
        self.mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_contours_style())
        
        self.mp_drawing.draw_landmarks(
            image=image,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_iris_connections_style())



if __name__ == "__main__":
    facemesh = FaceMesh()
    facemesh.startCapture()






