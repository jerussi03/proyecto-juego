"""Sprite extraction and AIR for Victor's single persistent stage actor."""
from pathlib import Path
import re
from PIL import Image,ImageDraw
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'chars/daniela/art/victor-assist'


def sprites():
    sheet=Image.open(ART/'sheet.png').convert('RGBA')
    frames={}
    # The complete figures in this sheet extend below nominal square cells.
    # These inspected row bands keep whole feet and leave the desk in place.
    bands=[(0,300),(300,558),(558,832),(832,sheet.height)]
    preview=Image.new('RGB',(1080,480),(26,35,43))
    for row,(top,bottom) in enumerate(bands):
        for col in range(6):
            cell=sheet.crop((col*256,top,(col+1)*256,bottom))
            cell.putalpha(cell.getchannel('A').point(lambda a:a if a>=60 else 0))
            pixels=np.array(cell)
            _,labels,stats,_=cv2.connectedComponentsWithStats((pixels[:,:,3]>80).astype(np.uint8),8)
            keep=np.isin(labels,[i for i in range(1,len(stats)) if stats[i,4]>=1000])
            pixels[:,:,3]*=keep
            cell=Image.fromarray(pixels)
            box=cell.getchannel('A').getbbox();assert box,(row,col)
            im=cell.crop(box);scale=.34
            im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
            axis_x=round((128-box[0])*scale)
            axis_y=round(((290 if row==0 else 550 if row==1 else 825 if row==2 else 997)-top-box[1])*scale)
            frames[8230+row,col]=(im,axis_x,axis_y)
            im.save(ART/f'{row}-{col}.png')
            preview.paste(im,(col*180+80-axis_x,row*120+110-axis_y),im)
    preview.save(ART/'preview.png')
    return frames


def install_air(path):
    text=path.read_text(encoding='utf-8')
    text=re.sub(r'(?s)\s*; BEGIN VICTOR ASSIST.*?; END VICTOR ASSIST\s*','\n',text)
    text=text.replace('; Victor persistent actor, desk and physical assist.','')
    text=re.sub(r'(?ims)^\[Begin Action 82\d\d\].*?(?=^\[Begin Action |^; BEGIN TEACHER SPECIALS|\Z)','',text)
    # All sitting/rising/running frames now share one source scale.
    out='\n; BEGIN VICTOR ASSIST\n'
    # Existing desk artwork includes typing, checking the phone and answering.
    # Keep a long typing section so calls read as occasional background work.
    desk=[(8201,i,12) for _ in range(3) for i in range(6)]
    desk += [(8202,i,18 if i not in [2,3,4] else 36) for i in range(6)]
    definitions={8200:[(8230,0,1)],8201:desk,8230:[(8230,i,5) for i in range(6)],
                 8231:[(8231,i,4) for i in range(6)],8232:[(8232,i,6) for i in range(6)],
                 8233:[(8233,0,-1)],8234:[(8230,i,5) for i in range(5,-1,-1)]}
    for action,frames in definitions.items():
        out+=f'\n[Begin Action {action}]\n'
        if action==8232:
            out+='Clsn1Default: 1\nClsn1[0] = 10,-95,70,-20\n'
        for group,index,ticks in frames:out+=f'{group},{index}, 0,0, {ticks}\n'
    path.write_text(text.rstrip()+'\n'+out+'; END VICTOR ASSIST\n',encoding='utf-8')
