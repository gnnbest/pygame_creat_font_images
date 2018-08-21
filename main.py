# _*_ coding: utf-8 _*_
import random
import pygame
import os
from pygame.locals import *
import cv2
pygame.init()# 必须要有，没有报错
import numpy as np

WORK_DIR = os.path.dirname(os.path.abspath(__file__))


label_path = os.path.join(WORK_DIR, "8_15_data/3750_words")
bg_img_path = os.path.join(WORK_DIR, "bg_imgs")
save_img_path = os.path.join(WORK_DIR, 'save_imgs')
fonts_path = os.path.join(WORK_DIR, "fonts")



# 获取背景列表
def get_list(path):
	for root, dir, files in os.walk(path):
		return files



# 所有文字生成一个字符串
def get_all_words( label_path ):

    total_words = ''

    with open(label_path) as f:

        lines = f.readlines()

        total_words = ''.join(lines)

        total_words = total_words.replace('\n', '')
        total_words = total_words.replace('\r', '')

    return total_words



size_min = 45
size_max = 110

bglist = get_list(bg_img_path)

font_list = get_list(fonts_path)

tup_colour = ((0, 0, 0), (255, 0, 255), (255, 0, 0), (0, 0, 255))

total_words = get_all_words(label_path)



# 随机生成文字surface
def get_font_surface(size):

    font = 'simhei.ttf'
    size = size
    tcolour = (0,0,0)

    #print(pygame.font.get_fonts())
    Font = pygame.font.Font(os.path.join(fonts_path, font), size)
    # 背景白色
    # rtext = Font.render(words, True, tcolour, (255,255,255))

    # 最后一个参数不添加，默认背景透明

    # rtext = Font.render(words, False, tcolour) # 字体带锯齿
    rtext_surface = Font.render(str(size), True, tcolour)  # 抗锯齿

    return rtext_surface



# 随机生成文字surface
def get_text_surface():

    num_words = random.randint(2, 20)
    str_start = random.randint(0, len(total_words) - 21)
    words = total_words[str_start:str_start + num_words]

    font = font_list[random.randint(0, len(font_list) - 1)]
    size = random.randint(size_min, size_max) // 10 * 10
    tcolour = random.choice(tup_colour)

#    Font = pygame.font.Font(font_list[random.randint(0, len(font_list))], size)
    Font = pygame.font.Font(os.path.join(fonts_path, font), size)
    # 背景白色
    # rtext = Font.render(words, True, tcolour, (255,255,255))

    # 最后一个参数不添加，默认背景透明

    # rtext = Font.render(words, False, tcolour) # 字体带锯齿
    rtext_surface = Font.render(words, True, tcolour)  # 抗锯齿
    tmp_surface = Font.render(words, True, tcolour, (255, 255, 255, 255))  # 抗锯齿

    return rtext_surface, tmp_surface




# 判断是否有交叉矩形
def is_intersect(extend_rect_list, extend_rect, bg_w, bg_h):

    state = False

    if (not(extend_rect[0] > 0 and extend_rect[1] > 0 and
        extend_rect[0]+extend_rect[2] < bg_w and extend_rect[1]+extend_rect[3] < bg_h)):
        state = True


    # 有一个交叉就不行
    for tmp_rect in  extend_rect_list:

        min_x = min(extend_rect[0], tmp_rect[0])
        max_x = max(extend_rect[0]+extend_rect[2], tmp_rect[0]+tmp_rect[2])

        if(max_x - min_x) >= (extend_rect[2] + tmp_rect[2]): # 未交叉

            continue

        else:

            state = True
            break

    return state



def scale_img(img):

    w, h = img.get_size()
    img_size = (w, h)
    im_size_min = np.min(img_size[0:2])
    im_size_max = np.max(img_size[0:2])

    im_scale = float(600) / float(im_size_min)

    if np.round(im_scale * im_size_max) > 1200:
        im_scale = float(1200) / float(im_size_max)

    w_new = int(w * im_scale)
    h_new = int(h * im_scale)

    img_new = pygame.transform.smoothscale(img, (w_new, h_new))  # 这种效果较好，边缘平滑

    return img_new



# 沿着y轴方向裁剪白色边框
def clip_white_space(img):

    w, h = img.get_size()
    top_y = 0
    bottom_y = 0
    is_top = False
    is_bottom = False

    for i in range(h):
        if is_top:
            break

        for j in range(w):
            value = img.get_at((j, i))
            if(value != (255,255,255,255)):
                top_y = i
                is_top = True
                break


    for i in range(h)[::-1]:
         if is_bottom:
            break

         for j in range(w)[::-1]:

             value = img.get_at((j, i))

             if (value != (255, 255, 255, 255)):
                 is_bottom = True
                 bottom_y = i
                 break

    return top_y, bottom_y



    
# 裁剪小图添加文字
def small_img_pending( bg_img, offset_y ):

    bg_w, bg_h = bg_img.get_size()

    num_loop = 50

    extend_w, extend_h = 8, 3

    extend_rect_list = []
    rect_list = []

    while(True):

        is_finish = False

        for i in range(num_loop):

            t_x = random.randint(extend_w+1, bg_w - (extend_w+1)) // 2 * 2
            t_y = random.randint(extend_h+1, bg_h - (extend_h+1))
    
            rtext_surface, tmp_surface = get_text_surface()
            t_w, t_h = rtext_surface.get_size()

            # 扩展后的矩形外接框（x, y, w, h）
            extend_rect = [(t_x-extend_w), (t_y-extend_h), t_w+2*extend_w, t_h+2*extend_h]

            if(not is_intersect(extend_rect_list, extend_rect, bg_w, bg_h)): # 若不相交可填充该文字框

                extend_rect_list.append(extend_rect)

                bg_img.blit(rtext_surface, (t_x, t_y))

                # 沿着文字边缘画矩形框
                top_y, bottom_y = clip_white_space(tmp_surface)
                t_y_min = max(0, top_y + t_y - 2)
                t_y_max = min(bg_h, bottom_y + t_y + 2)

                rect_list.append([t_x, t_y_min+offset_y, t_x + t_w, t_y_max+offset_y])

                #point_list = [[t_x,t_y_min],[t_x+t_w,t_y_min],[t_x+t_w,t_y_max],[t_x,t_y_max]]
                #pygame.draw.lines(bg_img, 0, True, point_list, 1)

                break

            elif(i == num_loop - 1): # 若循环10次还未找到地方，则该副图像填充完毕
                is_finish = True


        if(is_finish):
            break


    return bg_img, rect_list




# 一幅大图从上向下裁剪多幅小图分布进行填充
def img_pending(bg_img):

    w, h = bg_img.get_size()

    split_num = random.randint(4, 7)

    y_list = []

    y_inter = h // split_num

    rect_list = []

    for i in range(split_num):
        y = y_inter * i

        sub_rect = pygame.Rect(0, y, w, y_inter)

        sub_img = bg_img.subsurface(sub_rect).copy()

        sub_img, small_rect_list = small_img_pending(sub_img, y)

        rect_list.extend(small_rect_list)

        bg_img.blit(sub_img, (0, y))

    return bg_img, rect_list




# 主函数
def process(bg_img_path):

    for root, dirs, files in os.walk(bg_img_path):

        for i, filename in enumerate(files):

            try:
                org_bg_img = pygame.image.load(os.path.join(bg_img_path, filename))
                org_bg_img = scale_img(org_bg_img)
            except:
                os.remove(os.path.join(bg_img_path, filename))

                continue

            for k in range(4):

                bg_img = org_bg_img.copy()

                bg_img, rect_list = img_pending(bg_img)
            
                img_w, img_b = bg_img.get_size()

                save_filename = 'sample_' + str(i) + '_' + str(k) + '.jpg'

                #boxes = np.array(rect_list)
                #sub_make_xml(save_filename, img_w, img_b, boxes)


                pygame.image.save(bg_img, os.path.join(save_img_path, save_filename))




if __name__ == "__main__":

    process(bg_img_path)
