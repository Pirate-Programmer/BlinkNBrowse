import cv2 as cv
import mediapipe as mp
import math


#global settings (change em to gain fps on raspberry pi)
camera_input = 1
width = 640
height = 480
fps = 30
left_eye_coords = [33, 160, 158, 133, 153, 144]
right_eye_coords = [362, 385, 387, 263, 373, 380]
EAR_threshold = 0.2

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
            max_num_faces = 1,                #no of faces to be detected in frame
            refine_landmarks = True,         #better landmark details but cpu intensive 
            min_detection_confidence = 0.5,  #threshold for face detection
            min_tracking_confidence = 0.5,   #tracking across frames
        )

        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        
    

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
                    
                    print(f"Left Eye: {"Close" if self.EAR[0] < EAR_threshold else "Open"}")
                    print(f"Right Eye: {"Close" if self.EAR[1] < EAR_threshold else "Open"}")
                    frame.flags.writeable = True

                    frame = cv.flip(frame,1)
                    cv.putText(frame, f"Left Eye: {"Close" if self.EAR[1] < EAR_threshold else "Open"}",(w//2 - 300,h//2),cv.FONT_HERSHEY_COMPLEX,1.0, (0,255,0))
                    cv.putText(frame,f"Right Eye: {"Close" if self.EAR[0] < EAR_threshold else "Open"}",(w//2 - 300,h//2 + 50),cv.FONT_HERSHEY_COMPLEX,1.0, (0,255,0))

                   # self.drawLandmarks(result,frame)
                    cv.imshow("landmarks", frame)

                
            #exit on key press Q
            if cv.waitKey(10) & 0xFF == ord('q'):
                print("exiting ...")
                break

        #release the videocapture
        self.capture.release()

        #welp what the name says
        cv.destroyAllWindows()



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






