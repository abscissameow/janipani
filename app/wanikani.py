import time, math
from datetime import datetime
from converter import *
# import pandas as pd
import numpy as np
# from IPython.utils import io
# with io.capture_output() as captured:
#     import translators as ts


Delay = {-1:float('inf'),0:0,1: 4, 2: 8, 3: 24, 4: 48, 5: 168, 6: 336, 7: 720, 8: 2880, 9:float('inf')}

class rad:
    def __init__(self, link, hyerogliph, pic_path, meaning, mnemonics, lvl, stage=-1, previous_review=time.time(),extra=None):
        self.link=link
        self.hyerogliph=hyerogliph
        self.pic_path=pic_path
        self.meaning=meaning
        self.mnemonics=mnemonics
        self.lvl=lvl
        self.stage=stage
        self.previous_review=previous_review
        self.mnemonics_ru=extra if extra else ts.google(self.mnemonics, from_language='en', to_language='ru',timeout=60)
        self.ind_meaning=0
        self.ind_reading=1 
        self.type="rad"
    
    def make_ind_default(self):
        self.ind_meaning=0
        self.ind_reading=1

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class kan:
    def __init__(self, link, hyerogliph, meaning, kun_reading, on_reading, main_reading, mnemonics_meaning, mnemonics_reading, lvl, stage=-1, previous_review=time.time()):
        self.link=link
        self.hyerogliph=hyerogliph
        self.meaning=meaning
        self.kun_reading=kun_reading
        self.on_reading=on_reading
        self.mnemonics_meaning=mnemonics_meaning
        self.mnemonics_reading=mnemonics_reading
        self.main_reading=main_reading #KUN OR ON
        self.lvl=lvl
        self.stage=stage
        self.previous_review=previous_review
        self.mnemonics_meaning_ru=ts.google(self.mnemonics_meaning, from_language='en', to_language='ru',timeout=60)
        self.mnemonics_reading_ru=ts.google(self.mnemonics_reading, from_language='en', to_language='ru',timeout=60)
        self.ind_meaning=0
        self.ind_reading=0
        self.type="kan"  
    
    def make_ind_default(self):
        self.ind_meaning=0
        self.ind_reading=0

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class voc:
    def __init__(self, link, hyerogliph, meaning, reading, mnemonics_meaning, mnemonics_reading, context_sents, lvl ,stage=-1, previous_review=time.time()):
        self.link=link
        self.hyerogliph=hyerogliph
        self.meaning=meaning
        self.reading=reading
        self.mnemonics_meaning=mnemonics_meaning
        self.mnemonics_reading=mnemonics_reading
        self.context_sents=context_sents
        self.lvl=lvl
        self.stage=stage
        self.previous_review=previous_review
        self.mnemonics_meaning_ru=ts.google(self.mnemonics_meaning, from_language='en', to_language='ru',timeout=60)
        self.mnemonics_reading_ru=ts.google(self.mnemonics_reading, from_language='en', to_language='ru',timeout=60)
        self.ind_meaning=0
        self.ind_reading=0
        self.type="voc"  

    def make_ind_default(self):
        self.ind_meaning=0
        self.ind_reading=0 

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

randdict={0:'meaning',1:'reading'}
stage_to_str = {0:'Apprentice 0',1:'Apprentice 1', 2: 'Apprentice 2', 3: 'Apprentice 3', 4: 'Apprentice 4', 5: 'Guru 1', 6: 'Guru 2', 7: 'Master', 8: 'Enlightened', 9: 'Burned'}

def convert_(word,rand):
    return word if not rand else romajiToJapanese(word)


def review_forecast(): #for today and tomorrow
    zerozero=time.time()-(lambda x: int(x[:2])*3600+int(x[3:])*60)(datetime.now().strftime("%H:%M"))
    TODAY,TOMORROW,L={},{},[[],[]]
    for i in range(self.review_from,self.lvl+1):
            for j in self.DIC_ALL[i]:
                if not j.stage:
                    continue
                if (j.previous_time+Delay[j.stage]*3600-time.time())<=0:
                    L[0].append(j)
                    TODAY[-1]=TODAY.get(-1,0)+1
                    continue
                need_sec_from_zerozero=(j.previous_time+Delay[j.stage]*3600-zerozero)
                final_days, final_hour = need_sec_from_zerozero//(24*3600), math.ceil((need_sec_from_zerozero%(24*3600))/3600)
                if final_hour == 24:
                    final_days, final_hour = final_days+1, 0
                if final_days==0:
                    L[0].append(j)
                    TODAY[final_hour]=TODAY.get(final_hour,0)+1
                elif final_days==1:
                    L[1].append(j)
                    TOMORROW[final_hour]=TOMORROW.get(final_hour,0)+1
    if not TODAY:
        TODAY=pd.DataFrame([[0,0]],index=['00:00'],columns=['今日','SUM'])
        b=0
    else:
        a,b=map(list,zip(*sorted(TODAY.items())))
        a=list(map((lambda x: str(x)+':00' if x>10 else '0'+str(x)+':00'),a))
        a[0]='今' if a[0]=='0-1:00' else a[0]
        TODAY=pd.DataFrame(zip(b,np.cumsum(b)),index=a,columns=['今日','SUM'])
    if not TOMORROW:
        TOMORROW=pd.DataFrame([[0,np.sum(b)]],index=['00:00'],columns=['明日','SUM'])
    else:
        a1,b1=map(list,zip(*sorted(TOMORROW.items())))
        a1=list(map((lambda x: str(x)+':00' if x>10 else '0'+str(x)+':00'),a1))
        TOMORROW=pd.DataFrame(zip(b1,np.cumsum(b1)+np.sum(b)),index=a1,columns=['明日','SUM'])
    display(TODAY,TOMORROW)
    return L