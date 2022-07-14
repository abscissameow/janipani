import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time, random, math
from datetime import datetime
from IPython.display import clear_output
from converter import *
import pandas as pd
import numpy as np
from IPython.display import display
import pickle
from IPython.utils import io
with io.capture_output() as captured:
    import translators as ts


Delay = {0:float('inf'),1: 4, 2: 8, 3: 24, 4: 48, 5: 168, 6: 336, 7: 720, 8: 2880, 9:float('inf')}

def show_pic(item):
    img = mpimg.imread(item.pic)
    imgplot = plt.imshow(img)
    plt.axis('off')
    plt.show()

class rad:
    def __init__(self, lvl, pic, meaning, mnemonics='obvious', stage=0, previous_time=time.time()):
        self.previous_time=previous_time
        self.meaning=meaning #LIST
        self.stage=stage
        self.lvl=lvl
        self.pic=pic
        self.mnemonics=mnemonics 
        self.ind_meaning=0
        self.ind_reading=1 
        self.type="RADICAL"   

    def show(self,translate=False):
        print('名前: ',end='')
        print(*self.meaning,sep=', ')
        img = mpimg.imread(self.pic)
        imgplot = plt.imshow(img)
        plt.axis('off')
        plt.show()
        print('ニーモニック: ',self.mnemonics)
        if translate:
            print('\nニーモニック: ',ts.google(self.mnemonics, from_language='en', to_language='ru',timeout=10))
    
    def make_ind_default(self):
        self.ind_meaning=0
        self.ind_reading=1
    
    def info(self):
        show_pic(self)
        print('stage =',stage_to_str[self.stage],'(stage '+str(self.stage)+');','the symbol of',self.lvl,'lvl')
        print('previous review:',self.previous_time,'('+str(int((time.time()-self.previous_time)//3600))+' hours '+str(int(((time.time()-self.previous_time)%3600)//60))+' mins before now)')
        t=self.previous_time+Delay[self.stage]*3600-time.time()
        if t<0:
            print('you can review it right now!')
        elif t==float('inf'):
            print('no reviews available, learn it first in lessons!')
        else:
            print('next review in: ',int(t//3600),'hours',int((t%3600)//60),'mins')

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class kan:
    def __init__(self, lvl, pic, meaning, reading, mnemonics='obvious', stage=0, previous_time=time.time()):
        self.previous_time=previous_time
        self.meaning=meaning #LIST
        self.reading=reading #LIST
        self.lvl=lvl
        self.ind_meaning=0
        self.ind_reading=0
        self.stage=stage
        self.pic=pic
        self.mnemonics=mnemonics
        self.type="KANJI"  
    
    def show(self,translate=False):
        print('meanings: ',end='')
        print(*self.meaning,sep=', ')
        print('readings: ',end='')
        print(*self.reading,sep=', ')
        img = mpimg.imread(self.pic)
        imgplot = plt.imshow(img)
        plt.axis('off')
        plt.show()
        print('ニーモニック: ',self.mnemonics)
        if translate:
            print('\nニーモニック: ',ts.google(self.mnemonics, from_language='en', to_language='ru',timeout=10))

    def make_ind_default(self):
        self.ind_meaning=0
        self.ind_reading=0 
    
    def info(self):
        show_pic(self)
        print('stage =',stage_to_str[self.stage],'(stage '+str(self.stage)+');','the symbol of',self.lvl,'lvl')
        print('previous review:',self.previous_time,'('+str(int((time.time()-self.previous_time)//3600))+' hours '+str(int(((time.time()-self.previous_time)%3600)//60))+' mins before now)')
        t=self.previous_time+Delay[self.stage]*3600-time.time()
        if t<0:
            print('you can review it right now!')
        elif t==float('inf'):
            print('no reviews available, learn it first in lessons!')
        else:
            print('next review in: ',int(t//3600),'hours',int((t%3600)//60),'mins')

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class voc:
    def __init__(self, lvl, pic, meaning, reading, mnemonics='obvious',stage=0,previous_time=time.time()):
        self.previous_time=previous_time
        self.stage=stage
        self.ind_meaning=0
        self.ind_reading=0
        self.lvl=lvl
        self.pic=pic
        self.mnemonics=mnemonics
        self.meaning=meaning #LIST
        self.reading=reading #LIST
        self.type="VOCABULARY"  
    
    def show(self,translate=False):
        print('meanings: ',end='')
        print(*self.meaning,sep=', ')
        print('readings: ',end='')
        print(*self.reading,sep=', ')
        img = mpimg.imread(self.pic)
        imgplot = plt.imshow(img)
        plt.axis('off')
        plt.show()
        print('ニーモニック: ',self.mnemonics)
        if translate:
            print('\nニーモニック: ',ts.google(self.mnemonics, from_language='en', to_language='ru',timeout=10))

    def make_ind_default(self):
        self.ind_meaning=0
        self.ind_reading=0 
    
    def info(self):
        show_pic(self)
        print('stage =',stage_to_str[self.stage],'(stage '+str(self.stage)+');','the symbol of',self.lvl,'lvl')
        print('previous review:',self.previous_time,'('+str(int((time.time()-self.previous_time)//3600))+' hours '+str(int(((time.time()-self.previous_time)%3600)//60))+' mins before now)')
        t=self.previous_time+Delay[self.stage]*3600-time.time()
        if t<0:
            print('you can review it right now!')
        elif t==float('inf'):
            print('no reviews available, learn it first in lessons!')
        else:
            print('next review in: ',int(t//3600),'hours',int((t%3600)//60),'mins')

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

randdict={0:'meaning',1:'reading'}
stage_to_str = {0:'Apprentice 0',1:'Apprentice 1', 2: 'Apprentice 2', 3: 'Apprentice 3', 4: 'Apprentice 4', 5: 'Guru 1', 6: 'Guru 2', 7: 'Master', 8: 'Enlightened', 9: 'Burned'}

def convert_(word,rand):
    return word if not rand else romajiToJapanese(word)

def list_to_review(L):
    G=L.copy()
    for i in G:
        i.make_ind_default()
    L=L*2
    Wrongs_count={}
    while L:
        random.shuffle(L)
        item = L.pop()

        if item.ind_meaning and item.ind_reading:
            continue
        elif (not item.ind_meaning) and (not item.ind_reading):
            rand = random.randint(0,1)
        elif item.ind_meaning:
            rand = 1
        else:
            rand = 0
        
        clear_output(wait=True)
        show_pic(item)
        time.sleep(0.1)
        try:
            if (local:=convert_(input(randdict[rand].upper()+': ').lower(),rand)) in getattr(item,randdict[rand]) or (input("(≖_≖ ) 正しくない! YOUR INPUT WAS '" +str(local)+ "' MISSPELLED? 0/1")=='1'):
                item.previous_time=time.time()
                exec('item.ind_'+randdict[rand]+'=1')
                clear_output(wait=False)
                if item.ind_meaning and item.ind_reading:
                    if not item in Wrongs_count:
                        item.stage += item.stage + 1
                        print('NEW LVL OF THIS',item.type+':',stage_to_str[item.stage]+'!')
                    else:
                        item.stage=int(max(item.stage-(math.ceil(Wrongs_count[item]/2) * (1 if item.stage<5 else 2)),1))
                        print('LVL OF THIS',item.type+':',stage_to_str[item.stage]+'(')
                item.show()
                input("(⁀ᗢ⁀) 正しい! LETS GO NEXT!")
            elif (item in Wrongs_count) and (input("(┛ಠДಠ)┛彡┻━┻ SURRENDER?! 0/1")=='1'):
                item.previous_time=time.time()
                clear_output(wait=True)
                item.show()
                time.sleep(0.1)
                Wrongs_count[item]=Wrongs_count.get(item,0)+1
                L.append(item)
                input("(╥﹏╥) poor you.. so LETS GO NEXT!")
            else:
                item.previous_time=time.time()
                Wrongs_count[item]=Wrongs_count.get(item,0)+1
                L.append(item)
        except KeyboardInterrupt:
            for i in G:
                i.make_ind_default()
            raise KeyboardInterrupt
    for i in G:
        i.make_ind_default()
    return sum(Wrongs_count[key] for key in Wrongs_count)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def list_to_lesson(L,num,translate):
    try:
        for i in range(len(L)//num):
            for j in L[i*num:(i+1)*num]:
                clear_output(wait=True)
                j.show(translate)
                time.sleep(0.1)
                input("Lets go next!")
            input("ᕕ༼⌐■-■༽ᕗ Lets go review!")
            list_to_review(L[i*num:(i+1)*num])
        for i in L[num*(len(L)//num):]:
            clear_output(wait=True)
            i.show(translate)
            time.sleep(0.1)
            input("Lets go next!")
        if L[num*(len(L)//num):]:
            input("ᕕ༼⌐■-■༽ᕗ Lets go review!")
            list_to_review(L[num*(len(L)//num):])
    except KeyboardInterrupt:
        clear_output(wait=True)
        print("<(｀^´)> HEY! YOU DIDN'T FINISH!")
        return


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class wanikani:
    def __init__(self,DIC_RAD,DIC_KAN,DIC_VOC,DIC_ALL,DIC_NAMES,LVL=1,review_from=1):
        self.lvl=LVL
        self.review_from=review_from
        self.DIC_ALL=DIC_ALL
        self.DIC_RAD=DIC_RAD
        self.DIC_KAN=DIC_KAN
        self.DIC_VOC=DIC_VOC
        self.DIC_NAMES=DIC_NAMES

        self.ind_rad=1
        self.ind_kan=0
        self.ind_voc=0
    
    def help(self):
        print("wanikani class has the following methods:")
        print("account.lesson(N) -- activates avaliable lessons by rule: learn 'N' hieroglyphs a time and instantly review them")
        print("account.review -- activates avaliable reviews; if mistake was made several times you can 'surrender' and peep the answer")
        print("account.info -- returns basik info about account progress including avaliable lessons and reviews")
        print("account.review_forecast -- displays review forecast for today and tomorrow depending on your local time; also returns corresponding lists of hieroglyphs")
        print("account.refresh_everything(time) -- shifts back the time of the last review by 'time' seconds; (probably better dont use it)")
        print("if you want to see the more info about particular hieroglyph, use account.DIC_NAMES[(TYPE,MEANING)].info(), where the TYPE is the type of hieroglyph - 'rad','kan' or 'voc'")
    
    def info(self):
        c=0
        for i in self.DIC_KAN[self.lvl]:
            c = c+1 if i.stage>4 else c
        print('CURRENT LVL:',str(self.lvl)+'. PROGRESS:',c,"KANJI-GURU'S OUT OF",len(self.DIC_KAN[self.lvl]))
        print('NUM OF RADS IN THE LVL: '+str(len(self.DIC_RAD[self.lvl]))+'. KANS: '+str(len(self.DIC_KAN[self.lvl]))+'. VOCS:',len(self.DIC_VOC[self.lvl]))
        print('ACTIVE LESSONS:',self.count_lessons(),'\nACTIVE REVIEWS:',self.count_reviews())

    def refresh_everything(self,t=100000):
        for i in self.DIC_ALL:
            for j in self.DIC_ALL[i]:
                j.previous_time-=t

    def lesson(self, num=5, translate=False, save=True):
        L=[]
        if self.ind_rad:
            check=1
            for i in self.DIC_RAD[self.lvl]:
                if not i.stage:
                    L.append(i)
                    check=0
            if check:
                self.ind_kan=1
                self.ind_rad=0
        if self.ind_kan:
            check=1
            for i in self.DIC_KAN[self.lvl]:
                if not i.stage:
                    L.append(i)
                if i.stage<3:
                    check=0
            if check:
                self.ind_voc=1
                self.ind_kan=0
        if self.ind_voc:
            for i in self.DIC_VOC[self.lvl]:
                if not i.stage:
                    L.append(i)
        try:
            list_to_lesson(L,num,translate)
        except KeyboardInterrupt:
            clear_output(wait=True)
            print("<(｀^´)> HEY! YOU DIDN'T FINISH!")
            return
        finally:
            if save:
                FIT_DATAS=[self.DIC_RAD,self.DIC_KAN,self.DIC_VOC,self.DIC_ALL,self.DIC_NAMES,self.lvl,self.review_from]
                with open('FIT_DATAS.pkl', 'wb') as outp:
                    pickle.dump(FIT_DATAS, outp, pickle.HIGHEST_PROTOCOL)
        
    def review(self,save=True):
        L=[]
        for i in range(self.review_from,self.lvl+1):
            for j in self.DIC_ALL[i]:
                if (time.time()-j.previous_time)>=Delay[j.stage]*3600:
                    L.append(j)
        if not L:
            print("no reviews yet (っ˘̩╭╮˘̩)っ")
            return
        try:
            mistakes=list_to_review(L)
            clear_output(wait=True)
            if not mistakes:
                print("ᕙ(‾̀◡‾́)ᕗ 良い! NO MISTAKES OUT OF",str(len(L))+'!!')
            else:
                print("(─‿─) 良い!",mistakes,"MISTAKES OUT OF",str(len(L))+'!')
            if  self.islvlup():
                print("ヽ(♡‿♡)ノ LVL UP!, NOW IT IS",self.lvl)
        except KeyboardInterrupt:
            clear_output(wait=True)
            print("<(｀^´)> HEY! YOU DIDN'T FINISH!")
            if self.islvlup():
                print("ANYWAY.. (∿°○°)∿ LVL UP!, NOW IT IS",self.lvl)
        finally:
            if save:
                FIT_DATAS=[self.DIC_RAD,self.DIC_KAN,self.DIC_VOC,self.DIC_ALL,self.DIC_NAMES,self.lvl,self.review_from]
                with open('FIT_DATAS.pkl', 'wb') as outp:
                    pickle.dump(FIT_DATAS, outp, pickle.HIGHEST_PROTOCOL)
        

    def islvlup(self):
        count=0
        for i in self.DIC_KAN[self.lvl]:
            count = count+1 if (i.stage>4) else count
        if count==len(self.DIC_KAN[self.lvl]):
            self.lvl+=1
            self.ind_rad=1
            self.ind_kan=0
            self.ind_voc=0
            return True
        return False
    
    def count_lessons(self):
        c=0
        if self.ind_rad:
            for i in self.DIC_RAD[self.lvl]:
                if not i.stage:
                    c+=1
        if self.ind_kan:
            for i in self.DIC_KAN[self.lvl]:
                if not i.stage:
                    c+=1
        if self.ind_voc:
            for i in self.DIC_VOC[self.lvl]:
                if not i.stage:
                    c+=1
        return c

    def count_reviews(self):
        c=0
        for i in range(self.review_from,self.lvl+1):
            for j in self.DIC_ALL[i]:
                if (time.time()-j.previous_time)>=Delay[j.stage]*3600:
                    c+=1
        return c
    
    def review_forecast(self): #for today and tomorrow
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