import tkinter as tk
from tkinter import filedialog
import time
import os
import cv2
import numpy as np
import multiprocessing as mlp
from PIL import Image, ImageTk#图像控件
def s1_satting(value):
    global img1,canny,value1,value2, pic
    value1 = value
    canny= cv2.Canny(img1, int(value1), int(value2))
    opencv_image_gray = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
    pilImage=Image.fromarray(opencv_image_gray)
    pic = ImageTk.PhotoImage(image=pilImage)
def s2_satting(value):
    global img1,canny,value1,value2, pic
    value2 = value
    canny= cv2.Canny(img1, int(value1), int(value2))
    #cvimage = cv2.cvtColor(canny, cv2.COLOR_BGR2RGBA)
    opencv_image_gray = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
    pilImage=Image.fromarray(opencv_image_gray)
    pic = ImageTk.PhotoImage(image=pilImage)
def quit():
    global key
    key=False
#打开文件夹
def opendir():
    global file, last_file
    
    nfile = filedialog.askopenfilename(initialdir=os.getcwd())
    if len(nfile) == 0:
        file = last_file
    else:
        file = nfile
        last_file = nfile
    print(file)
    if file !=None:
        pic_process()
#图片处理
def pic_process():
    global file, w, h, pic, img1, canny, photo, x1_value
    Img = cv2.imread(file)
    size = Img.shape
    #获取图片的宽高
    w = size[1] #宽度
    h = size[0] #高度
    x1_value = w
    img1 = cv2.GaussianBlur(Img,(3,3),0)
    canny = cv2.Canny(img1, value1, value2)
    opencv_image_gray = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
    pilImage=Image.fromarray(opencv_image_gray)
    pic = ImageTk.PhotoImage(image=pilImage)
    photo = tk.PhotoImage(file=file)

#线长限制
def line_restrict():
    global line_len, top
    Line_restrict = tk.Toplevel(top)
    Line_restrict.geometry("200x80")     
    Line_restrict.config(bg="white")
    line_scale = tk.Scale(Line_restrict,
                          from_=0,
                          to=20,
                          resolution =1,
                          label = "低于此长度的线段将被舍去",
                          length =200,
                          sliderlength= 20,
                          width = 8,
                          orient=tk.HORIZONTAL, 
                          repeatdelay=0, 
                          command = line_len_change
                          )
    line_scale.set(value=line_len)
    line_scale.pack()
    Line_restrict.mainloop

def line_len_change(value):
    global line_len
    line_len = int(value)

#Gcode 生成
def Gcode_create():
    global canny, line_len, file, Gcode_create_log,contours, w, x1_value, x0_init, y0_init
    if file == None:
        gcode_create_err = tk.Toplevel(top)
        gcode_create_err.geometry("200x150")     
        gcode_create_err.config(bg="white")
        frame = tk.Frame(gcode_create_err)
        frame.pack(side="top", anchor="se",)
        err = tk.Label(frame, font=("Arial", 25),text = "请先打开文件")
        err.pack(side="top")
        gcode_create_err.mainloop()
    else:
        static_code = ['G21','G90','G92 X0Y0','S1000','F3000','G0Z0','M5','G4 P0.2']
        contours, hierarchy = cv2.findContours(
        canny, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_NONE)
        file1=open('test.txt','w')
        file1.write(str(contours))
        for LINE in contours:
            file1.write(str(LINE))
            file1.write('\n\n\n\n')
        file1.close
        file = open('result.gcode','w')
        for code in static_code:
            file.write(code)
            file.write('\n')
        linenum=0
        for line in contours:
            if len(line) >= line_len: 
                if linenum!=0:
                    file.write("G1G90 Z0.0F6000\n")
                    file.write("G0 X"+str(round(int(x0_init)+line[0][0][0]*(int(x1_value)/int(w)),3))+"Y"+str(round(int(y0_init)+line[0][0][1]*(int(x1_value)/int(w)),3))+"\n")
                    file.write("G1G90 Z4.0F6000\n")
                for dot in line:
                    file.write('G1 '+'X'+str(round(int(x0_init)+dot[0][0]*(int(x1_value)/int(w)),3))+'Y'+str(int(y0_init)+round(dot[0][1]*(int(x1_value)/int(w)),3)))
                    file.write('\n')
                linenum+=1
        file.write("G1G90 Z0.0F6000\n")
        file.write("G90G0 X0Y0\n")
        file.close()
        Gcode_create_log = True
        print("create over!")
def threshold_window():
    global value1, value2, top, file
    
    Threshold_window = tk.Toplevel(top)
    Threshold_window.geometry("200x150")     
    Threshold_window.config(bg="white")
    if file == None:
        frame = tk.Frame(Threshold_window)
        frame.pack(side="top", anchor="se",)

        # 创建日期标签
        err = tk.Label(frame, font=("Arial", 25),text = "请先打开文件")
        err.pack(side="top")
    else:
        s1=tk.Scale(Threshold_window, 
                from_ =0,
                to =255,resolution =1,
                length =200,
                sliderlength= 20,
                width = 8,
                orient=tk.HORIZONTAL, 
                repeatdelay=0, 
                label = "threshold1",
                command = s1_satting
                )
        s1.pack(side = "top",anchor= "sw", expand=True)
        s1.set(value=value1)
        s2=tk.Scale(Threshold_window, 
                from_ =0, 
                to =255,
                resolution =1,
                length =200,
                sliderlength= 20, 
                width = 8, 
                orient=tk.HORIZONTAL, 
                repeatdelay=0, 
                label = "threshold2",
                command = s2_satting)
        s2.pack(side = "top",anchor= "sw", expand=True)
        s2.set(value=value2)

def size_setting():
    global x1_value
    size_window = tk.Toplevel(top)
    size_window.geometry("200x150")     
    size_window.config(bg="white")
    frame = tk.Frame(size_window)
    frame.pack(side="top", anchor="se",)
    if file == None:

        # 创建日期标签
        err = tk.Label(frame, font=("Arial", 25),text = "请先打开文件")
        err.pack(side="top")
    else:
        x1=tk.Scale(size_window, 
                from_ =50,
                to =500,resolution =1,
                length =200,
                sliderlength= 20,
                width = 8,
                orient=tk.HORIZONTAL, 
                repeatdelay=0, 
                label = "x/mm",
                command = x1_setting
                )
        x1.pack(side = "top")
        x1.set(value=x1_value)

        y1_label = tk.Label(frame, font=("Arial", 12),text = "y的值将随x同比例增大缩小")
        y1_label.pack(side="left",anchor="nw")

def x1_setting(value):
    global x1_value
    x1_value = value
def Preview():
    global Gcode_create_log, w, h, preview_log,contours, line_len,canvas2, dot_sum,dot_num,preview_canny
    if Gcode_create_log == False:
        gcode_create_err = tk.Toplevel(top)
        gcode_create_err.geometry("200x150")     
        gcode_create_err.config(bg="white")
        frame = tk.Frame(gcode_create_err)
        frame.pack(side="top", anchor="se",)
        err = tk.Label(frame, font=("Arial", 20),text = "请先生成Gcode")
        err.pack(side="top")
        gcode_create_err.mainloop()
    else:
        dot_sum = 0
        dot_num = 0
        for LINE in contours:
            dot_sum+=len(LINE)
        preview_canny = np.zeros((h,w),dtype=np.uint8)
        preview_log = True

def dot_create():
    global contours,dot_sum,dot_num,preview_canny,pre_pic
    temp_dot = dot_num
    for LINE in contours:
        if temp_dot<len(LINE):
            preview_canny[LINE[temp_dot][0][1]][LINE[temp_dot][0][0]] = np.uint8(255)
            opencv_image_GRAY = cv2.cvtColor(preview_canny, cv2.COLOR_GRAY2RGB)
            pilImage=Image.fromarray(opencv_image_GRAY)
            pre_pic = ImageTk.PhotoImage(image=pilImage)
            break
        else: temp_dot -= len(LINE)
    dot_num +=1

def init_location():
    global x0_init, y0_init
    IL_window = tk.Toplevel(top)
    IL_window.geometry("200x150")     
    IL_window.config(bg="white")
    s_1=tk.Scale(IL_window, 
                from_ =0,
                to =200,resolution =1,
                length =200,
                sliderlength= 20,
                width = 8,
                orient=tk.HORIZONTAL, 
                repeatdelay=0, 
                label = "x0",
                command = x0_setting
                )
    s_1.pack(side = "top",anchor= "sw", expand=True)
    s_1.set(value=x0_init)
    s_2=tk.Scale(IL_window, 
                from_ =0,
                to =200,resolution =1,
                length =200,
                sliderlength= 20,
                width = 8,
                orient=tk.HORIZONTAL, 
                repeatdelay=0, 
                label = "y0",
                command = y0_setting
                )
    s_2.pack(side = "top",anchor= "sw", expand=True)
    s_2.set(value=y0_init)

def x0_setting(value):
    global x0_init
    x0_init=value
def y0_setting(value):
    global y0_init
    y0_init=value

def g_g_main(
               ):
    global key, canny, value1, value2, pic, file, w, h, top, line_len, last_file, Gcode_create_log, preview_log,photo,canvas2,pre_pic,x0_init,y0_init
    value1 = 50
    value2 = 150
    top = tk.Tk()
    top.geometry("1020x700")     
    top.config(bg="white")
    key=True
    file = None
    last_file = None
    cvimage = None
    line_len = 10
    Gcode_create_log = False
    preview_log = False
    x0_init = 0
    y0_init = 0
    photo = None
    #frame = tk.Frame(top)
    #frame.pack(side="bottom", anchor="se",)
    
    
    #blur = cv2.GaussianBlur(img, (3, 3), 0)

    #button
    button_frame=tk.Frame(top)
    button_frame.pack(side='top',fill=tk.X)

    button_openfile = tk.Button(button_frame, text="open file",command=opendir)
    button_openfile.pack(side='left')

    button_threshold_setting = tk.Button(button_frame, text="threshold setting",command=threshold_window)
    button_threshold_setting.pack(side='left')

    button_line_restrict = tk.Button(button_frame, text="line restrict",command=line_restrict)
    button_line_restrict.pack(side='left')

    button_line_restrict = tk.Button(button_frame, text="init_location",command=init_location)
    button_line_restrict.pack(side='left')

    button_line_restrict = tk.Button(button_frame, text="size_setting",command=size_setting)
    button_line_restrict.pack(side='left')

    button_gcode_create = tk.Button(button_frame, text="gcode_generate",command=Gcode_create)
    button_gcode_create.pack(side='left')
    button_preview = tk.Button(button_frame, text="preview", command=Preview)
    button_preview.pack(side='left')
    #画布
    canvas1 = tk.Canvas(top, width=500, height=700)
    canvas1.pack(anchor= "nw",side = "left")
    canvas2 = tk.Canvas(top, width=500, height=700)
    canvas2.pack(anchor= "nw",side = "right")
    

    while True:
        if file != None and photo!=None:
            canvas1.create_image((w/2, h/2), image=photo)
            if preview_log == False:
                canvas2.create_image((w/2, h/2), image=pic)
            else:
                dot_create()
                canvas2.create_image((w/2, h/2), image=pre_pic)
                


        top.update()
        time.sleep(0.1)
        top.protocol("WM_DELETE_WINDOW", quit)
        if not key:
            print("quit")
            break
if __name__ == "__main__":
    g_g_main()