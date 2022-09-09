from cgi import test
from kivy.lang import Builder
from kivy.clock import Clock
import random
from kivymd.app import MDApp
from wanikani import *
import pickle, random
from kivy.core.audio import SoundLoader

TEST=False

def save():
	if TEST:
		return
	with open('DATA.pkl', 'wb') as outp:
		pickle.dump(DATA, outp, pickle.HIGHEST_PROTOCOL)
	with open('CHALLENGE.pkl', 'wb') as outp:
		pickle.dump(CHALLENGE, outp, pickle.HIGHEST_PROTOCOL)
if TEST:
	with open('DATATEST.pkl', 'rb') as inp:
		DATA=pickle.load(inp)
else:
	with open('DATA.pkl', 'rb') as inp:
		DATA=pickle.load(inp)

# def reset():
# 	for i in range(60):
# 		for j in DATA[i].values():
# 			for k in j:
# 				k.previous_review-=3600*24*60
# 				k.stage=-1
# 	global CHALLENGE
# 	CHALLENGE=[0, datetime.now()]
# 	save()
# #reset() 

try:
    with open('CHALLENGE.pkl', 'rb') as inp:
    	CHALLENGE=pickle.load(inp)
except:
	CHALLENGE=[0, datetime.now()]
	save()

def inlatin(word):
	for i in word:
		if (i<'a' or i>'z') and (i<'0' or i>'9') and (i!=' '):
			return False
	return True

def updateCHALLENGE():
	global CHALLENGE
	date_format = "%m/%d/%Y"
	today = datetime.strptime(datetime.now().strftime(date_format), date_format)
	prev = datetime.strptime(CHALLENGE[1].strftime(date_format), date_format)
	if (today-prev).days>=1:
		CHALLENGE[0]=0
		CHALLENGE[1]=datetime.now()
		save()

jap_nums={11:'',0:'',1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'七',8:'八',9:'九',10:'十'}
def numtojap(n):
	sign = '-' if n<0 else ''
	n=abs(n)
	thous,hunds,tens,ons=n//1000,(n%1000)//100,(n%100)//10,n%10
	if hunds == 1:
		hunds=11
	if tens == 1:
		tens=11
	if thous == 1:
		thous=11
	res=(thous>0)*(jap_nums[thous]+'千')+(hunds>0)*(jap_nums[hunds]+'百')+(tens>0)*(jap_nums[tens]+'十')+(ons>0)*jap_nums[ons]
	if not res:
		return '零'
	return sign+res
	

def forecast(lvl):
	latest=DATA[0]['rad'][0].previous_review + Delay[DATA[0]['rad'][0].stage]*3600
	for i in range(lvl):
		for hyes in DATA[i].values():
			for k in hyes:
				if k.previous_review + Delay[k.stage]*3600 < latest:
					latest = k.previous_review + Delay[k.stage]*3600
	latest = max(0,(latest-time.time())//60)
	return f"next review in {int(latest//60)}h {int(latest%60)}m"

def distance(inpword,trueword,numbercheck=True):
		inpword,trueword=inpword.strip(),trueword.strip()
		linp,ltrue=len(inpword),len(trueword)
		if numbercheck:
			inp,tru=[],[]
			for i in range(linp):
				if inpword[i]>='0' and inpword[i]<='9':
					inp.append(inpword[i])
			for i in range(ltrue):
				if trueword[i]>='0' and trueword[i]<='9':
					tru.append(trueword[i])
			if inp!=tru:
				return 100

		D = np.zeros((linp+1, ltrue+1))
		for i in range(linp+1):
			for j in range(ltrue+1):
				if i==0:
					D[i,j]=j
				elif j==0:
					D[i,j]=i
				else:
					D[i,j]=min(D[i-1,j]+1, D[i,j-1]+1, D[i-1,j-1] + 1 - (inpword[i-1]==trueword[j-1]))
		return D[linp,ltrue]

def sortby(text,L):
	L.sort(key = lambda hye: min(distance(text, meaning, False) for meaning in (hye.meaning if isinstance(hye.meaning, list) else [hye.meaning])))
	return L

def is_it(input, answers, indicator):
	if indicator:
		return input in answers	
	# def compare(inp_word,true_word):
	# 	mistakes=0
	# 	dictrue,dicinp = {},{}
	# 	for i in true_word:
	# 		if i in dictrue: 
	# 			dictrue[i] += 1
	# 		else: 
	# 			dictrue[i] = 1
	# 	for i in inp_word:
	# 		if i in dicinp: 
	# 			dicinp[i] += 1
	# 		else: 
	# 			dicinp[i] = 1
	# 	for i in dictrue:
	# 		if i not in dicinp:
	# 			if i>='0' and i<='9':
	# 				return 10
	# 			mistakes+=dictrue[i]
	# 			continue
	# 		mistakes+=abs(dictrue[i]-dicinp[i])
	# 	for i in dicinp:
	# 		if i not in dictrue:
	# 			if i>='0' and i<='9':
	# 				return 10
	# 			mistakes+=dicinp[i]/2
	# 			continue
	# 		mistakes+=abs(dictrue[i]-dicinp[i])/2
	# 	return int(mistakes)
	for phrase in answers:
		if distance(input,phrase)<=(1 if len(phrase)<=5 else 2 if len(phrase)<=9 else 3):
			return True
	return False

def list_reviews(DATA,lvl,reviews):
	L=[]
	for i in range(lvl):
		for j in DATA[i].values():
			for hye in j:
				if hye.type=='rad':
					if hye.ind_meaning:
						continue
				elif hye.ind_meaning or hye.ind_reading:
					continue
				if hye in reviews:
					continue
				if (time.time()-hye.previous_review)>=Delay[hye.stage]*3600:
					L.append(hye)
	random.shuffle(L)
	return L

def list_lessons(DATA,lvl):
	L=[]
	if TEST:
		for i in DATA[1].values():
			for j in i:
				if j.stage==-1 and j.type!='rad':
					L.append(j)
		return L
	for radical in DATA[lvl-1]['rad']:
		if radical.stage==-1:
			L.append(radical)
	if not L:
		mult=0.9
		kan3=0
		for kanji in DATA[lvl-1]['kan']:
			if kanji.stage==-1:
				L.append(kanji)
			elif kanji.stage>=3:
				kan3+=1
		if (kan3>=len(DATA[lvl-1]['kan'])*mult) or sum([1 if i.stage>=0 else 0 for i in DATA[lvl-1]['voc']]):
			for vocab in DATA[lvl-1]['voc']:
				if vocab.stage==-1:
					L.append(vocab)
	return L

def Lvl():
	mult=0.9
	lvl=1
	for lv in range(59):
		if (sum([1 if i.stage>=5 else 0 for i in DATA[lv]['kan']])>=len(DATA[lv]['kan'])*mult) and (sum([1 if i.stage>=3 else 0 for i in DATA[lv]['kan']])==len(DATA[lv]['kan'])) and \
			(sum([1 if i.stage>=2 else 0 for i in DATA[lv]['voc']])==len(DATA[lv]['voc'])) or sum([1 if i.stage>=0 else 0 for i in DATA[lv+1]['kan']]) or sum([1 if i.stage>=0 else 0 for i in DATA[lv+1]['rad']]):
			lvl+=1
		else:
			return lvl
	if (sum([1 if i.stage>=5 else 0 for i in DATA[59]['kan']])>=len(DATA[59]['kan'])*mult) and (sum([1 if i.stage>=2 else 0 for i in DATA[lv]['kan']])==len(DATA[lv]['kan'])):
			return lvl+1
	return lvl

def count_stages(lvl):
	appr,guru,master,enl,burn=0,0,0,0,0
	for i in range(lvl):
		for j in DATA[i].values():
			for k in j:
				if k.stage>0:
					if k.stage<5:
						appr+=1
					elif k.stage<7:
						guru+=1
					elif k.stage==7:
						master+=1
					elif k.stage==8:
						enl+=1
					else:
						burn+=1
	return str(appr),str(guru),str(master),str(enl),str(burn)

# def fill_daily_hyes(obj,n=10):
# 	if obj.daily_hyes:
# 		return obj.daily_hyes
# 	if (datetime.now()-CHALLENGE[1]).days>=1:
# 		CHALLENGE[0]=0
# 		CHALLENGE[1]=datetime.now()
# 	hyes=[]
# 	CHALLENGE[0]=min(CHALLENGE[0],n)
# 	if CHALLENGE[0]<n:
# 		for lvl in range(obj.lvl):
# 			for j in DATA[lvl].values():
# 				for k in j:
# 					hyes.append(k)
# 	n=min(len(hyes),n)
# 	return [] if not hyes else random.sample(hyes,n)
def getvoc(maxlvl,n):
	hyes=[]
	for i in range(maxlvl):
			for k in DATA[i]['voc']:
				if k.stage>=0:
					hyes.append(k)
	return random.sample(hyes, n)

colors={'rad':(0,163/255,245/255,1),'kan':(252/255,84/255,148/255,1),'voc':(96/255, 0, 144/255,1)}
class MainApp(MDApp):	
	lvl=Lvl()
	lessons=[]
	reviews=[]
	reviews_pack=[]
	pack_size=10
	hye_review=None
	rand=None
	Wrongs_count={}
	infos=[]
	refresh_shield=0
	hye_info=None
	# daily_hyes=[]
	hye_challenge=None
	rand_challenge=None
	hye_lesson=None
	type_challenge=None
	truebutton=None

	def build(self):
		self.theme_cls.theme_style = "Dark"
		self.theme_cls.primary_palette = "Pink"
		self.theme_cls.primary_hue='200'

		for i in range(self.lvl):
			for j in DATA[i].values():
				for k in j:
					k.make_ind_default()
		
		return Builder.load_file('kvkv.kv')

	def press_lesson_tab(self):
		if not self.lessons:
			self.root.ids.play_lesson.text="LET'S CAKE!"
		self.theme_cls.primary_palette = "Pink"
		self.theme_cls.primary_hue='200'
	def press_review_tab(self):
		if not self.reviews:
			self.root.ids.play_review.text="LET'S CAKE!"
		self.theme_cls.primary_palette = "Cyan"
		self.theme_cls.primary_hue='500'
	def press_info_tab(self):
		self.root.ids.search.font_size=80
		self.root.ids.search.text=''
		self.root.ids.forecast.text = forecast(self.lvl)
		# self.root.ids.forecast.md_bg_color=self.theme_cls.primary_color
		self.root.ids.Apprentice.text,self.root.ids.Guru.text,self.root.ids.Master.text,self.root.ids.Enlightened.text,self.root.ids.Burned.text=count_stages(self.lvl)
		loc=sum([1 if i.stage>=5 else 0 for i in DATA[self.lvl-1]['kan']])+sum([1 if i.stage>=2 else 0 for i in DATA[self.lvl-1]['voc']])
		self.root.ids.progress.text=f'Your level is {self.lvl}'
		self.root.ids.progress_bar.value=100*loc/(len(DATA[self.lvl-1]['kan'])+len(DATA[self.lvl-1]['voc']))
		self.root.ids.search.current_hint_text_color=self.theme_cls.primary_color
		self.root.ids.search.hint_text="  enter _help"
		self.root.ids.active_lessons.text = f'Active lessons: {len(list_lessons(DATA,self.lvl))}'
		self.root.ids.active_reviews.text = f'Active reviews: {len(self.reviews)+len(list_reviews(DATA,self.lvl,self.reviews))}'
		self.theme_cls.primary_palette = "DeepPurple"
		self.theme_cls.primary_hue='300'
	def press_challenge_tab(self):
		if self.lvl<2:
			self.theme_cls.primary_palette = "Indigo"
			self.theme_cls.primary_hue='400'
			self.challenge_disable()
			return
		self.challenge_enable()
		if not self.hye_challenge:
			self.newtask()
		self.theme_cls.primary_palette = "Indigo"
		self.theme_cls.primary_hue='400'
	
	def hide_everything_lesson(self):
		self.root.ids.lesson_sound.opacity=0
		self.root.ids.lesson_sound.disabled=True
		self.root.ids.play_lesson.opacity=0
		self.root.ids.play_lesson.text=''
		self.root.ids.next_lesson_button.opacity=0
		self.root.ids.next_lesson_button.disabled=True
		self.root.ids.next_lesson.text=''
		self.root.ids.accordion.opacity=0
		self.root.ids.info_mdcard.opacity=0
		self.root.ids.mdcard_lesson.opacity=0
		self.root.ids.play_lesson_button.opacity=0
		self.root.ids.play_lesson_button.disabled=True
	
	def sound_lesson(self):
		name=self.hye_lesson.link.replace('://','-').replace('/','_')
		sound = SoundLoader.load('wav/'+name+'.wav')
		sound.play()

	def press_lesson_cake(self):
		self.lessons=list_lessons(DATA,self.lvl)
		if not self.lessons:
			self.hide_everything_lesson()
			self.root.ids.play_lesson.opacity=1
			self.root.ids.play_lesson.text='NO CAKES!'
			self.root.ids.play_lesson_button.opacity=1
			self.root.ids.play_lesson_button.disabled=False
			return
		
		self.hide_everything_lesson()
		
		self.root.ids.info_mdcard.opacity=1
		self.root.ids.accordion.opacity=1
		self.root.ids.mdcard_lesson.opacity=1
		self.root.ids.mdcard_lesson_rad.opacity=1
		
		
		self.root.ids.next_lesson.text="cake next!"
		self.root.ids.next_lesson_button.opacity=1
		self.root.ids.next_lesson_button.disabled=False

		hye=self.lessons.pop(0)

		if hye.type=='voc':
			self.root.ids.lesson_sound.opacity=1
			self.root.ids.lesson_sound.disabled=False

		self.hye_lesson=hye
		self.root.ids.mdcard_lesson.md_bg_color=colors[hye.type]
		if hye.type=='rad':
			self.root.ids.meaning.text = "Meaning: "+hye.meaning
			self.root.ids.kun_reading.text=''
			self.root.ids.on_reading.text=''
			self.root.ids.mnemonics_meaning.text=hye.mnemonics
			self.root.ids.mnemonics_meaning_ru.text=hye.mnemonics_ru
			self.root.ids.mnemonics_reading.text=""
			self.root.ids.mnemonics_reading_ru.text=""
			if not hye.hyerogliph:
				self.root.ids.mdcard_lesson.opacity=0
				self.root.ids.rad_pic_lesson.source=hye.pic_path
			else:
				self.root.ids.hyerogliph_lesson.text=hye.hyerogliph
				self.root.ids.mdcard_lesson_rad.opacity=0
		elif hye.type=='kan':
			self.root.ids.mdcard_lesson_rad.opacity=0
			if hye.main_reading=='kun':
				self.root.ids.on_reading.theme_text_color='Hint'
				self.root.ids.kun_reading.theme_text_color='Primary'
			elif hye.main_reading=='on':
				self.root.ids.kun_reading.theme_text_color='Hint'
				self.root.ids.on_reading.theme_text_color='Primary'
			else:
				self.root.ids.on_reading.theme_text_color='Primary'
				self.root.ids.kun_reading.theme_text_color='Primary'
				self.root.ids.meaning.text+=' '+hye.main_reading

			self.root.ids.meaning.text = "Meaning: "+', '.join(hye.meaning)
			self.root.ids.kun_reading.text="Kun'yomi reading: "+', '.join(hye.kun_reading)
			self.root.ids.on_reading.font_size=self.root.ids.kun_reading.font_size
			self.root.ids.on_reading.text="On'yomi reading: "+', '.join(hye.on_reading)
			self.root.ids.mnemonics_meaning.text=hye.mnemonics_meaning
			self.root.ids.mnemonics_meaning_ru.text=hye.mnemonics_meaning_ru
			self.root.ids.mnemonics_reading.text=hye.mnemonics_reading
			self.root.ids.mnemonics_reading_ru.text=hye.mnemonics_reading_ru
			self.root.ids.hyerogliph_lesson.text=hye.hyerogliph
		else:
			self.root.ids.on_reading.theme_text_color='Primary'
			self.root.ids.kun_reading.theme_text_color='Primary'
			self.root.ids.mdcard_lesson_rad.opacity=0
			self.root.ids.meaning.text = "Meaning: "+', '.join(hye.meaning)
			self.root.ids.kun_reading.text="Reading: "+', '.join(hye.reading)
			# self.root.ids.on_reading.font_size=self.root.ids.kun_reading.font_size*0.8
			# self.root.ids.on_reading.text="Example: "+hye.context_sents[0]+f'\n({hye.context_sents[1]})'
			self.root.ids.on_reading.text=''
			self.root.ids.mnemonics_meaning.text=hye.mnemonics_meaning
			self.root.ids.mnemonics_meaning_ru.text=hye.mnemonics_meaning_ru
			self.root.ids.mnemonics_reading.text=hye.mnemonics_reading
			self.root.ids.mnemonics_reading_ru.text=hye.mnemonics_reading_ru
			self.root.ids.hyerogliph_lesson.text=hye.hyerogliph

		hye.stage=0
		save()
	
	#----------------------------------------------------------------------------------------------
	#----------------------------------------------------------------------------------------------
	
	def hide_everything_review(self):
		self.root.ids.review_sound.opacity=0
		self.root.ids.review_sound.disabled=True

		self.root.ids.refresh_button.disabled=True
		self.root.ids.refresh_button.opacity=0
		self.root.ids.play_review_button.opacity=0
		self.root.ids.play_review_button.disabled=True
		self.root.ids.play_review.text=''
		self.root.ids.surrender_review_button.opacity=0
		self.root.ids.surrender_review_button.disabled=True
		self.root.ids.mdcard_review.opacity=0
		self.root.ids.mdcard_review_rad.opacity=0
		self.root.ids.input.disabled=True
		self.root.ids.input.opacity=0
		self.root.ids.meaning_reading.text=''
		self.root.ids.input.helper_text=''
		self.root.ids.input.error=False
		self.root.ids.stage_review.opacity=0
		self.root.ids.stage_review.disabled=True

		self.root.ids.next_lesson_button_review.opacity=0
		self.root.ids.next_lesson_button_review.disabled=True
		self.root.ids.next_lesson_review.text=''
		self.root.ids.accordion_review.opacity=0
		self.root.ids.info_mdcard_review.opacity=0
		self.root.ids.mdcard_lesson_review.opacity=0
	
	def sound_review(self):
		name=self.hye_review.link.replace('://','-').replace('/','_')
		sound = SoundLoader.load('wav/'+name+'.wav')
		sound.play()

	def press_review_cake(self):
		self.root.ids.refresh_button.icon='refresh'
		self.root.ids.input.error=False
		new_reviews=list_reviews(DATA,self.lvl,self.reviews)
		self.reviews+=new_reviews
		self.reviews_pack=self.reviews[:self.pack_size]
		random.shuffle(self.reviews_pack)
		
		self.hide_everything_review()
		
		if not self.reviews:
			# self.root.ids.correct.opacity=0
			self.root.ids.play_review.text='NO CAKES!'
			self.root.ids.play_review_button.opacity=1
			self.root.ids.play_review_button.disabled=False
			return

		self.root.ids.stage_review.opacity=1
		self.root.ids.stage_review.disabled=False

		self.root.ids.refresh_button.disabled=False
		self.root.ids.refresh_button.opacity=1
		self.root.ids.input.opacity=1
		self.root.ids.input.disabled=False
		self.root.ids.surrender_review_button.opacity=1
		self.root.ids.surrender_review_button.disabled=False
		
		
		self.hye_review=self.reviews_pack[0]#!!!
		self.root.ids.stage_review.text=stage_to_str[self.hye_review.stage]
		if (not self.hye_review.ind_meaning) and (not self.hye_review.ind_reading):
			self.rand = random.randint(0,1)
		elif self.hye_review.ind_meaning:
			self.rand = 1
		else:
			self.rand = 0
		
		self.root.ids.meaning_reading.text=randdict[self.rand]
		self.root.ids.mdcard_review.md_bg_color=colors[self.hye_review.type]
		self.root.ids.mdcard_review_rad.md_bg_color=colors[self.hye_review.type]
		if not self.hye_review.hyerogliph:
			self.root.ids.rad_pic_review.source=self.hye_review.pic_path
			self.root.ids.mdcard_review_rad.opacity=1
			self.root.ids.mdcard_review.opacity=0
		else:
			self.root.ids.hyerogliph_review.text=self.hye_review.hyerogliph
			self.root.ids.mdcard_review_rad.opacity=0
			self.root.ids.mdcard_review.opacity=1
	
	def correct(self,dt):
		self.root.ids.correct.opacity=0
		self.root.ids.surrender_review_button.md_bg_color=self.theme_cls.primary_color
		self.root.ids.refresh_button.md_bg_color=self.theme_cls.primary_color
		# self.theme_cls.primary_palette = "Cyan"
		# self.theme_cls.primary_hue='500'
		self.root.ids.input.line_color_normal=(1,1,1,1)


	def press_input(self):
		self.refresh_shield=0
		# self.root.ids.input.helper_text=''
		if 'NOOO! not' in self.root.ids.input.text:
			self.root.ids.input.text=''
			self.root.ids.input.error=False
			self.press_review_cake()
			return
		m=[]
		if self.hye_review.type=='rad':
			l=[self.hye_review.meaning]
		elif not self.rand:
			l=self.hye_review.meaning
		elif self.hye_review.type=='kan':
			if self.hye_review.main_reading=='kun':
				l=self.hye_review.kun_reading
				m=self.hye_review.on_reading
			elif self.hye_review.main_reading=='on':
				l=self.hye_review.on_reading
				m=self.hye_review.kun_reading
			else:
				l=[self.hye_review.main_reading[8:]]
		else:
			l=self.hye_review.reading
		
		text=convert_(self.root.ids.input.text.lower(), self.rand).strip()
		kat=convert_('*'+self.root.ids.input.text.lower(),self.rand).strip()
		if is_it(text, l, self.rand) or (kat in l):
			if self.rand and self.hye_review.type=='voc':
				name=self.hye_review.link.replace('://','-').replace('/','_')
				sound = SoundLoader.load('wav/'+name+'.wav')
				sound.play()
			if not self.rand and self.hye_review.type=='voc':
				if self.hye_review.link=='http://wanikani.com/vocabulary/%E4%B8%96':
					sound = SoundLoader.load('EXTRA/'+'THE WORLD'+'.wav')
					sound.play()
				elif self.hye_review.link=='http://wanikani.com/vocabulary/%E9%87%91':
					sound = SoundLoader.load('EXTRA/'+'GOLD EXPERIENCE'+'.wav')
					sound.play()

			self.root.ids.correct.opacity=1
			# self.theme_cls.primary_palette = "LightGreen"
			# self.theme_cls.primary_hue='A700'
			self.root.ids.surrender_review_button.md_bg_color=(0,226/255,0,1)
			self.root.ids.refresh_button.md_bg_color=(0,226/255,0,1)
			self.root.ids.input.line_color_normal=(0,226/255,0,1)
			Clock.schedule_once(self.correct, 1.1)
			exec('self.hye_review.ind_'+randdict[self.rand]+'=1')
			mult=0.9
			if self.hye_review.ind_meaning and self.hye_review.ind_reading:
				assert(time.time()-self.hye_review.previous_review >= Delay[self.hye_review.stage]*3600)
				self.hye_review.previous_review=time.time()
				self.reviews.pop(self.reviews.index(self.hye_review))
				self.hye_review.make_ind_default()
				if not self.hye_review in self.Wrongs_count:
					self.hye_review.stage += 1
				else:
					self.hye_review.stage=int(max(self.hye_review.stage-(math.ceil(self.Wrongs_count[self.hye_review]/2) * (1 if self.hye_review.stage<5 else 2)),1))
				save()
				self.Wrongs_count.pop(self.hye_review, None)
			if (sum([1 if i.stage>=5 else 0 for i in DATA[self.lvl-1]['kan']])>=len(DATA[self.lvl-1]['kan'])*mult) and (sum([1 if i.stage>=3 else 0 for i in DATA[self.lvl-1]['kan']])==len(DATA[self.lvl-1]['kan'])) and \
				(sum([1 if i.stage>=2 else 0 for i in DATA[self.lvl-1]['voc']])==len(DATA[self.lvl-1]['voc'])):
				self.lvl+=1
			save()
		else:
			n=[]
			if self.hye_review.type!='rad':
				if self.hye_review.type=='kan':
					n=self.hye_review.meaning if self.rand else self.hye_review.kun_reading+self.hye_review.on_reading
				else:
					n=self.hye_review.meaning if self.rand else self.hye_review.reading
			
			if convert_(self.root.ids.input.text.lower(), self.rand) in m:
				self.root.ids.meaning_reading.text = f"oops! I am looking for {self.hye_review.main_reading}'yomi reading!"
				self.root.ids.input.text=''
				return
			
			if (self.root.ids.input.text.lower() in n) or (convert_(self.root.ids.input.text.lower(),not self.rand) in n):
				self.root.ids.meaning_reading.text = f"oops! I am looking for {randdict[self.rand].capitalize()}!"
				self.root.ids.input.text=''
				return
			self.root.ids.input.error_color= (225/255,0,64/255,1)
			self.root.ids.refresh_button.icon='shield-refresh'
			self.Wrongs_count[self.hye_review]=self.Wrongs_count.get(self.hye_review,0)+1
			self.root.ids.input.error=True
			self.root.ids.input.helper_text=''
			self.root.ids.input.text=f'NOOO! not {convert_(self.root.ids.input.text.lower(),self.rand)}!'
			return
		self.root.ids.input.text=''
		self.press_review_cake()

	def press_refresh(self):
		if self.refresh_shield:
			return
		if self.root.ids.input.error:
			if self.hye_review not in self.Wrongs_count:
				return
			self.refresh_shield=1
			self.root.ids.input.helper_text='   i mean ok but its like you know'
			self.root.ids.input.error_color= (1, 233/255, 130/255, 1)
			self.root.ids.input.text=''
			self.root.ids.refresh_button.icon='refresh'
			self.Wrongs_count[self.hye_review]-=1
			if not self.Wrongs_count[self.hye_review]:
				del self.Wrongs_count[self.hye_review]
			return
		self.root.ids.input.text=''
		self.press_review_cake()



	def press_review_surrender(self):
		self.refresh_shield=0
		if self.hye_review not in self.Wrongs_count:
			self.Wrongs_count[self.hye_review]=1
	
		self.hide_everything_review()

		self.root.ids.input.disabled=True
		self.root.ids.info_mdcard_review.opacity=1
		self.root.ids.accordion_review.opacity=1
		self.root.ids.mdcard_lesson_review.opacity=1
		self.root.ids.mdcard_lesson_rad_review.opacity=1
		self.root.ids.next_lesson_button_review.opacity=1
		self.root.ids.next_lesson_button_review.disabled=False
		self.root.ids.next_lesson_review.text=""

		hye=self.hye_review
		if hye.type=='voc':
			self.root.ids.review_sound.opacity=1
			self.root.ids.review_sound.disabled=False
		
		self.root.ids.mdcard_lesson_review.md_bg_color=colors[hye.type]
		if hye.type=='rad':
			self.root.ids.meaning_review.text = "Meaning: "+hye.meaning
			self.root.ids.kun_reading_review.text=''
			self.root.ids.on_reading_review.text=''
			self.root.ids.mnemonics_meaning_review.text=hye.mnemonics
			self.root.ids.mnemonics_meaning_ru_review.text=hye.mnemonics_ru
			self.root.ids.mnemonics_reading_review.text=""
			self.root.ids.mnemonics_reading_ru_review.text=""
			if not hye.hyerogliph:
				self.root.ids.mdcard_lesson_review.opacity=0
				self.root.ids.rad_pic_lesson_review.source=hye.pic_path
			else:
				self.root.ids.hyerogliph_lesson_review.text=hye.hyerogliph
				self.root.ids.mdcard_lesson_rad_review.opacity=0
		elif hye.type=='kan':
			if hye.main_reading=='kun':
				self.root.ids.on_reading_review.theme_text_color='Hint'
				self.root.ids.kun_reading_review.theme_text_color='Primary'
			elif hye.main_reading=='on':
				self.root.ids.kun_reading_review.theme_text_color='Hint'
				self.root.ids.on_reading_review.theme_text_color='Primary'
			else:
				self.root.ids.on_reading_review.theme_text_color='Primary'
				self.root.ids.kun_reading_review.theme_text_color='Primary'
				self.root.ids.meaning_review.text+=' '+hye.main_reading
			self.root.ids.mdcard_lesson_rad_review.opacity=0
			self.root.ids.meaning_review.text = "Meaning: "+', '.join(hye.meaning)
			self.root.ids.kun_reading_review.text="Kun'yomi reading: "+', '.join(hye.kun_reading)
			self.root.ids.on_reading_review.font_size=self.root.ids.kun_reading.font_size
			self.root.ids.on_reading_review.text="On'yomi reading: "+', '.join(hye.on_reading)
			self.root.ids.mnemonics_meaning_review.text=hye.mnemonics_meaning
			self.root.ids.mnemonics_meaning_ru_review.text=hye.mnemonics_meaning_ru
			self.root.ids.mnemonics_reading_review.text=hye.mnemonics_reading
			self.root.ids.mnemonics_reading_ru_review.text=hye.mnemonics_reading_ru
			self.root.ids.hyerogliph_lesson_review.text=hye.hyerogliph
		else:
			self.root.ids.on_reading_review.theme_text_color='Primary'
			self.root.ids.kun_reading_review.theme_text_color='Primary'
			self.root.ids.mdcard_lesson_rad_review.opacity=0
			self.root.ids.meaning_review.text = "Meaning: "+', '.join(hye.meaning)
			self.root.ids.kun_reading_review.text="Reading: "+', '.join(hye.reading)
			# self.root.ids.on_reading_review.font_size=self.root.ids.kun_reading.font_size*0.8
			# self.root.ids.on_reading_review.text="Example: "+hye.context_sents[0]+f'\n({hye.context_sents[1]})'
			self.root.ids.on_reading_review.text=''
			self.root.ids.mnemonics_meaning_review.text=hye.mnemonics_meaning
			self.root.ids.mnemonics_meaning_ru_review.text=hye.mnemonics_meaning_ru
			self.root.ids.mnemonics_reading_review.text=hye.mnemonics_reading
			self.root.ids.mnemonics_reading_ru_review.text=hye.mnemonics_reading_ru
			self.root.ids.hyerogliph_lesson_review.text=hye.hyerogliph

	def press_lesson_cake_review(self):
		self.root.ids.input.text=''
		self.press_review_cake()
	
	def stage_button(self):
		if self.root.ids.stage_review.text==stage_to_str[self.hye_review.stage]:
			t=time.time()-self.hye_review.previous_review
			self.root.ids.stage_review.text=str(round(t//(3600*24)))+'d '+ str(round((t-round(t//(3600*24))*3600*24)//3600))+'h'
		else:
			self.root.ids.stage_review.text=stage_to_str[self.hye_review.stage]
	
	#----------------------------------------------------------------------------------------------

	def hide_everything_info(self):
		self.root.ids.forecast.opacity=0
		self.root.ids.progress.opacity=0
		self.root.ids.Stages.opacity=0
		self.root.ids.search.disabled=True
		self.root.ids.search.opacity=0
		self.root.ids.info.opacity=0
		self.root.ids.progress.text=''
		self.root.ids.progress_under.text=''
		self.root.ids.progress_bar.opacity=0
		self.root.ids.mdcard_lesson_rad_info.opacity=0
		self.root.ids.stage_info.opacity=0
		self.root.ids.stage_info.disabled=True
		
		
		self.root.ids.info_sound.opacity=0
		self.root.ids.info_sound.disabled=True
		self.root.ids.info_next.opacity=0
		self.root.ids.info_next.disabled=True
		self.root.ids.next_lesson_button_info.opacity=0
		self.root.ids.next_lesson_button_info.disabled=True
		self.root.ids.next_lesson_info.text=''
		self.root.ids.accordion_info.opacity=0
		self.root.ids.info_mdcard_info.opacity=0
		self.root.ids.mdcard_lesson_info.opacity=0
	
	def press_lesson_cake_info(self):
		mult=0.9
		self.hide_everything_info()
		self.root.ids.forecast.opacity=1
		self.root.ids.forecast.text = forecast(self.lvl)
		self.root.ids.progress.opacity=1
		loc=sum([1 if i.stage>=5 else 0 for i in DATA[self.lvl-1]['kan']])+sum([1 if i.stage>=2 else 0 for i in DATA[self.lvl-1]['voc']])
		self.root.ids.progress.text=f'Your level is {self.lvl}'
		self.root.ids.progress_under.text='guru kanji '+str(loc)+'/'+str(len(DATA[self.lvl-1]['kan']))
		self.root.ids.progress_bar.value=100*loc/(len(DATA[self.lvl-1]['kan'])+len(DATA[self.lvl-1]['voc']))
		self.root.ids.progress_bar.opacity=1
		self.root.ids.search.current_hint_text_color=self.theme_cls.primary_color
		self.root.ids.search.hint_text="  enter _help"
		self.root.ids.search.text=''
		self.root.ids.search.disabled=False
		self.root.ids.search.opacity=1
		self.root.ids.info.opacity=1
		self.root.ids.active_lessons.text = f'Active lessons: {len(list_lessons(DATA,self.lvl))}'
		self.root.ids.active_reviews.text = f'Active reviews: {len(self.reviews)+len(list_reviews(DATA,self.lvl,self.reviews))}'
		self.root.ids.Stages.opacity=1
		self.root.ids.Apprentice.text,self.root.ids.Guru.text,self.root.ids.Master.text,self.root.ids.Enlightened.text,self.root.ids.Burned.text=count_stages(self.lvl)

		
	def search(self,indicator):
		if indicator==0:
			try:
				self.root.ids.search.font_size=80
				self.root.ids.search.hint_text="  enter _help"
				if self.root.ids.search.text=="ENTER: 'meaning' / 'type meaning' / 'lvl n' / '_spread n'(hours)":
					self.root.ids.search.text=''
					return
				if self.root.ids.search.text=='_help':
					self.root.ids.search.hint_text=''
					self.root.ids.search.font_size=50
					self.root.ids.search.text="ENTER: 'meaning' / 'type meaning' / 'lvl n' / '_spread n'(hours)"
					return
				self.infos=[]
				L=self.root.ids.search.text.lower().split(' ',1)
				
				if L[0]=='_review':
					lvl,type,hye=L[1].split(' ')
					for i in DATA[int(lvl)-1][type]:
						if hye in i.meaning:
							i.previous_review=time.time()-10000*3600
							save()
							self.root.ids.search.text+=' done'
							return

				elif L[0]=='_spread':
					t=time.time()
					delta=int(L[1])
					for i in range(self.lvl):
						for j in DATA[i].values():
							for h in j:
								r=random.randint(0,delta)
								if t-h.previous_review>=r*3600:
									h.previous_review+=r*3600
					save()
					self.root.ids.search.text+=' done'
					return
				# elif L[0]=='show' and len(L)>1:
				# 	maxl=int(L[1])
				# 	for i in range(self.lvl):
				# 		for hyes in DATA[i].values():
				# 			for k in hyes:
				# 				if len(self.infos)<maxl:
				# 					self.infos.append(k)
				# 				else:
				# 					for j in range(maxl):
				# 						better = k.previous_review + Delay[k.stage]*3600 < self.infos[j].previous_review + Delay[self.infos[j].stage]*3600
				# 						if (k not in self.infos) and better:
				# 							self.infos[j]=k
				# elif L[0]=='_set':
				# 	lvl,typ,h,to=L[1].split(' ')
				# 	for i in DATA[int(lvl)-1][typ]:
				# 		if h in i.meaning:
				# 			i.stage=int(to)
				# 			save()
				# 			self.root.ids.search.text+=' done'
				# 			return
				# elif L[0]=='_time_reset':
				# 	lvl,typ,h=L[1].split(' ')
				# 	for i in DATA[int(lvl)-1][typ]:
				# 		if h in i.meaning:
				# 			i.previous_review=time.time()-1000*3600
				# 			save()
				# 			self.root.ids.search.text+=' done'
				# 			return
				elif L[0]=='lvl':
					self.infos=[item for sublist in DATA[int(L[1])-1].values() for item in sublist]
				elif L[0] not in ['rad','kan','voc']:
					if inlatin(self.root.ids.search.text.lower()):
						for i in range(60):
							for hyes in DATA[i].values():
								for hye in hyes:
									for meaning in (lambda x: [x] if hye.type=='rad' else x)(hye.meaning):
										if self.root.ids.search.text.lower() in meaning:
											self.infos.append(hye)
											break
					else:
						for i in range(60):
							for hyes in DATA[i].values():
								for hye in hyes:
									if hye.type=='rad':
										continue
									if hye.type=='voc':
										for reading in hye.reading:
											if self.root.ids.search.text in reading:
												self.infos.append(hye)
												break
									else:
										for reading in (hye.on_reading+hye.kun_reading):
											if reading and (self.root.ids.search.text in reading):
												self.infos.append(hye)
												break

				else:
					type,text = L
					if inlatin(text):
						for i in range(60):
							for hye in DATA[i][type]:
								for meaning in (lambda x: [x] if type=='rad' else x)(hye.meaning):
									if text in meaning:
										self.infos.append(hye)
										break
					else:
						for i in range(60):
							for hye in DATA[i][type]:
								if hye.type=='rad':
									continue
								if hye.type=='voc':
									for reading in hye.reading:
										if text in reading:
											self.infos.append(hye)
											break
								else:
									for reading in (hye.on_reading+hye.kun_reading):
										if reading and (text in reading):
											self.infos.append(hye)
											break
				if not self.infos:
					self.root.ids.search.current_hint_text_color=(225/255,0,64/255,1)
					self.root.ids.search.hint_text=f"  couldn't find relevant: '{self.root.ids.search.text}'"
					self.root.ids.search.text=''
					return
			except:
				self.root.ids.search.current_hint_text_color=(225/255,0,64/255,1)
				self.root.ids.search.hint_text=f"  couldn't find relevant: '{self.root.ids.search.text}'"
				self.root.ids.search.text=''
				return
		else:
			if not self.infos:
				self.press_lesson_cake_info()
				return
		
		self.infos=sortby(self.root.ids.search.text,self.infos)

		self.hide_everything_info()
		
		self.root.ids.info_next.opacity=1
		self.root.ids.info_next.disabled=False
		self.root.ids.info_mdcard_info.opacity=1
		self.root.ids.accordion_info.opacity=1
		self.root.ids.mdcard_lesson_info.opacity=1
		self.root.ids.mdcard_lesson_rad_info.opacity=1
		self.root.ids.next_lesson_button_info.opacity=1
		self.root.ids.next_lesson_button_info.disabled=False
		self.root.ids.next_lesson_info.text=""

		hye=self.infos.pop(0)

		if hye.type=='voc':
			self.root.ids.info_sound.opacity=1
			self.root.ids.info_sound.disabled=False

		self.hye_info=hye

		self.root.ids.stage_info.opacity=1
		self.root.ids.stage_info.disabled=False
		self.root.ids.stage_info.text=stage_to_str[hye.stage] if hye.stage!=(-1) else 'not explored'

		self.root.ids.mdcard_lesson_info.md_bg_color=colors[hye.type]

		if hye.type=='rad':
			self.root.ids.meaning_info.text = "Meaning: "+hye.meaning
			self.root.ids.kun_reading_info.text=''
			self.root.ids.on_reading_info.text=''
			self.root.ids.mnemonics_meaning_info.text=hye.mnemonics
			self.root.ids.mnemonics_meaning_ru_info.text=hye.mnemonics_ru
			self.root.ids.mnemonics_reading_info.text=""
			self.root.ids.mnemonics_reading_ru_info.text=""
			if not hye.hyerogliph:
				self.root.ids.mdcard_lesson_info.opacity=0
				self.root.ids.rad_pic_lesson_info.source=hye.pic_path
			else:
				self.root.ids.hyerogliph_lesson_info.text=hye.hyerogliph
				self.root.ids.mdcard_lesson_rad_info.opacity=0
		elif hye.type=='kan':
			if hye.main_reading=='kun':
				self.root.ids.on_reading_info.theme_text_color='Hint'
				self.root.ids.kun_reading_info.theme_text_color='Primary'
			elif hye.main_reading=='on':
				self.root.ids.kun_reading_info.theme_text_color='Hint'
				self.root.ids.on_reading_info.theme_text_color='Primary'
			else:
				self.root.ids.on_reading_info.theme_text_color='Primary'
				self.root.ids.kun_reading_info.theme_text_color='Primary'
				self.root.ids.meaning_info.text+=' '+hye.main_reading
			self.root.ids.mdcard_lesson_rad_info.opacity=0
			self.root.ids.meaning_info.text = "Meaning: "+', '.join(hye.meaning)
			self.root.ids.kun_reading_info.text="Kun'yomi reading: "+', '.join(hye.kun_reading)
			self.root.ids.on_reading_info.font_size=self.root.ids.kun_reading.font_size
			self.root.ids.on_reading_info.text="On'yomi reading: "+', '.join(hye.on_reading)
			self.root.ids.mnemonics_meaning_info.text=hye.mnemonics_meaning
			self.root.ids.mnemonics_meaning_ru_info.text=hye.mnemonics_meaning_ru
			self.root.ids.mnemonics_reading_info.text=hye.mnemonics_reading
			self.root.ids.mnemonics_reading_ru_info.text=hye.mnemonics_reading_ru
			self.root.ids.hyerogliph_lesson_info.text=hye.hyerogliph
		else:
			self.root.ids.on_reading_info.theme_text_color='Primary'
			self.root.ids.kun_reading_info.theme_text_color='Primary'
			self.root.ids.mdcard_lesson_rad_info.opacity=0
			self.root.ids.meaning_info.text = "Meaning: "+', '.join(hye.meaning)
			self.root.ids.kun_reading_info.text="Reading: "+', '.join(hye.reading)
			# self.root.ids.on_reading_info.font_size=self.root.ids.kun_reading.font_size*0.8
			# self.root.ids.on_reading_info.text="Example: "+hye.context_sents[0]+f'\n({hye.context_sents[1]})'
			self.root.ids.on_reading_info.text=''
			self.root.ids.mnemonics_meaning_info.text=hye.mnemonics_meaning
			self.root.ids.mnemonics_meaning_ru_info.text=hye.mnemonics_meaning_ru
			self.root.ids.mnemonics_reading_info.text=hye.mnemonics_reading
			self.root.ids.mnemonics_reading_ru_info.text=hye.mnemonics_reading_ru
			self.root.ids.hyerogliph_lesson_info.text=hye.hyerogliph
		
	def sound_info(self):
		name=self.hye_info.link.replace('://','-').replace('/','_')
		sound = SoundLoader.load('wav/'+name+'.wav')
		sound.play()

	def info_next(self):
		if not self.infos:
			return
		self.search(1)

	def stage_info_button(self):
		stage = stage_to_str[self.hye_info.stage] if (self.hye_info.stage>=0) else 'not explored'
		if self.hye_info.stage==-1:
			t=residual=0
		else:
			t=self.hye_info.previous_review+Delay[self.hye_info.stage]*3600-time.time()
			residual=str(round(t//(3600)))+'h '+ str(round((t-round(t//(3600))*3600)//60))+'m'
		if self.root.ids.stage_info.text==stage:
			if self.hye_info.stage==-1:
				self.root.ids.stage_info.text='∞ h'
			else:
				self.root.ids.stage_info.text=residual
		elif self.root.ids.stage_info.text in [residual,'∞ h']:
			# if self.hye_info.stage==-1:
			# 	self.root.ids.stage_info.text='not exists'
			# else:
			# 	t=time.time()-self.hye_info.previous_review
			# 	self.root.ids.stage_info.text=str(round(t//(3600*24)))+'d '+ str(round((t-round(t//(3600*24))*3600*24)//3600))+'h'
			self.root.ids.stage_info.text='lvl '+str(self.hye_info.lvl)
		else:
			self.root.ids.stage_info.text=stage
	#----------------------------------------------------------------------------------------------
	def hide_everything_challenge(self):
		self.root.ids.mdcard_meaning_reading_challenge.opacity=0

		self.root.ids.challenge_sound.opacity=0
		self.root.ids.challenge_sound.disabled=True
	
	def challenge_disable(self):
		self.root.ids.challenge_sound.opacity=0
		self.root.ids.challenge_sound.disabled=True

		self.root.ids.mdcard_meaning_reading_challenge.opacity=1
		self.root.ids.meaning_reading_challenge.text='LOCKED\n(get lvl 2 to unlock)'
		self.root.ids.meaning_reading_challenge.font_size=40
		self.root.ids.mdcard_meaning_reading_challenge.pos_hint['center_y']=0.5

		self.root.ids.mdcard_counter_challenge.opacity=0

		self.root.ids.button_challenge1.opacity=0
		self.root.ids.button_challenge1.disabled=True
		self.root.ids.button_challenge2.opacity=0
		self.root.ids.button_challenge2.disabled=True
		self.root.ids.button_challenge3.opacity=0
		self.root.ids.button_challenge3.disabled=True
		self.root.ids.button_challenge4.opacity=0
		self.root.ids.button_challenge4.disabled=True
	
	def challenge_enable(self):
		self.root.ids.mdcard_counter_challenge.opacity=1
		self.root.ids.meaning_reading_challenge.font_size=60
		self.root.ids.mdcard_meaning_reading_challenge.pos_hint['center_y']=.7

		self.root.ids.button_challenge1.opacity=1
		self.root.ids.button_challenge1.disabled=False
		self.root.ids.button_challenge2.opacity=1
		self.root.ids.button_challenge2.disabled=False
		self.root.ids.button_challenge3.opacity=1
		self.root.ids.button_challenge3.disabled=False
		self.root.ids.button_challenge4.opacity=1
		self.root.ids.button_challenge4.disabled=False
		

	
	def newtask(self):
		self.hide_everything_challenge()
		self.root.ids.mdcard_counter_challenge_text.text=numtojap(CHALLENGE[0])
		dice=random.randint(1,6)
		self.type_challenge=2 if dice == 1 else 3 if dice <= 3 else 1 

		self.hye_challenge=getvoc(self.lvl,1)[0]
		a,b,c=getvoc(self.lvl,3)
		self.truebutton=random.randint(1,4)
		if self.type_challenge==1:#reading->meaning?
			self.root.ids.mdcard_meaning_reading_challenge.opacity=1
			self.root.ids.meaning_reading_challenge.text=self.hye_challenge.reading[0]
			meanings=[a.meaning[0],b.meaning[0],c.meaning[0]]
			while self.hye_challenge.meaning[0] in meanings or len(set(meanings))<3:
				a,b,c=getvoc(self.lvl,3)
				meanings=[a.meaning[0],b.meaning[0],c.meaning[0]]
			if self.truebutton==1:
				self.root.ids.button_challenge1.text=self.hye_challenge.meaning[0]
				self.root.ids.button_challenge2.text=meanings[0]
				self.root.ids.button_challenge3.text=meanings[1]
				self.root.ids.button_challenge4.text=meanings[2]
			elif self.truebutton==2:
				self.root.ids.button_challenge2.text=self.hye_challenge.meaning[0]
				self.root.ids.button_challenge1.text=meanings[0]
				self.root.ids.button_challenge3.text=meanings[1]
				self.root.ids.button_challenge4.text=meanings[2]
			elif self.truebutton==3:
				self.root.ids.button_challenge3.text=self.hye_challenge.meaning[0]
				self.root.ids.button_challenge1.text=meanings[0]
				self.root.ids.button_challenge2.text=meanings[1]
				self.root.ids.button_challenge4.text=meanings[2]
			elif self.truebutton==4:
				self.root.ids.button_challenge4.text=self.hye_challenge.meaning[0]
				self.root.ids.button_challenge1.text=meanings[0]
				self.root.ids.button_challenge2.text=meanings[1]
				self.root.ids.button_challenge3.text=meanings[2]
		elif self.type_challenge==2:#meaning->hye?
			self.root.ids.mdcard_meaning_reading_challenge.opacity=1
			self.root.ids.meaning_reading_challenge.text=self.hye_challenge.meaning[0]
			hyes=[a.hyerogliph,b.hyerogliph,c.hyerogliph]
			while self.hye_challenge.hyerogliph in hyes or len(set(hyes))<3:
				a,b,c=getvoc(self.lvl,3)
				hyes=[a.hyerogliph,b.hyerogliph,c.hyerogliph]
			if self.truebutton==1:
				self.root.ids.button_challenge1.text=self.hye_challenge.hyerogliph
				self.root.ids.button_challenge2.text=hyes[0]
				self.root.ids.button_challenge3.text=hyes[1]
				self.root.ids.button_challenge4.text=hyes[2]
			elif self.truebutton==2:
				self.root.ids.button_challenge2.text=self.hye_challenge.hyerogliph
				self.root.ids.button_challenge1.text=hyes[0]
				self.root.ids.button_challenge3.text=hyes[1]
				self.root.ids.button_challenge4.text=hyes[2]
			elif self.truebutton==3:
				self.root.ids.button_challenge3.text=self.hye_challenge.hyerogliph
				self.root.ids.button_challenge1.text=hyes[0]
				self.root.ids.button_challenge2.text=hyes[1]
				self.root.ids.button_challenge4.text=hyes[2]
			elif self.truebutton==4:
				self.root.ids.button_challenge4.text=self.hye_challenge.hyerogliph
				self.root.ids.button_challenge1.text=hyes[0]
				self.root.ids.button_challenge2.text=hyes[1]
				self.root.ids.button_challenge3.text=hyes[2]
		else:#sound_reading->meaning?
			self.root.ids.challenge_sound.opacity=1
			self.root.ids.challenge_sound.disabled=False
			meanings=[a.meaning[0],b.meaning[0],c.meaning[0]]
			while self.hye_challenge.meaning[0] in meanings or len(set(meanings))<3:
				a,b,c=getvoc(self.lvl,3)
				meanings=[a.meaning[0],b.meaning[0],c.meaning[0]]
			if self.truebutton==1:
				self.root.ids.button_challenge1.text=self.hye_challenge.meaning[0]
				self.root.ids.button_challenge2.text=meanings[0]
				self.root.ids.button_challenge3.text=meanings[1]
				self.root.ids.button_challenge4.text=meanings[2]
			elif self.truebutton==2:
				self.root.ids.button_challenge2.text=self.hye_challenge.meaning[0]
				self.root.ids.button_challenge1.text=meanings[0]
				self.root.ids.button_challenge3.text=meanings[1]
				self.root.ids.button_challenge4.text=meanings[2]
			elif self.truebutton==3:
				self.root.ids.button_challenge3.text=self.hye_challenge.meaning[0]
				self.root.ids.button_challenge1.text=meanings[0]
				self.root.ids.button_challenge2.text=meanings[1]
				self.root.ids.button_challenge4.text=meanings[2]
			elif self.truebutton==4:
				self.root.ids.button_challenge4.text=self.hye_challenge.meaning[0]
				self.root.ids.button_challenge1.text=meanings[0]
				self.root.ids.button_challenge2.text=meanings[1]
				self.root.ids.button_challenge3.text=meanings[2]

	def challenge_sound(self):
		name=self.hye_challenge.link.replace('://','-').replace('/','_')
		sound = SoundLoader.load('wav/'+name+'.wav')
		sound.play()

	def button_challenge(self,n):
		updateCHALLENGE()
		if self.truebutton == n:
			self.correct_challenge()
		else:
			self.incorrect_challenge()
		self.newtask()
	
	def correct_challenge(self):
		CHALLENGE[0]+=1
		CHALLENGE[1]=datetime.now()
		self.root.ids.mdcard_counter_challenge_text.text=numtojap(CHALLENGE[0])
		self.root.ids.correct_challenge.opacity=1
		self.root.ids.correct_challenge1.opacity=1
		save()
		Clock.schedule_once(self.correct_challenge1, 1.1)
	def incorrect_challenge(self):
		CHALLENGE[0]-=1
		CHALLENGE[1]=datetime.now()
		self.root.ids.mdcard_counter_challenge_text.text=numtojap(CHALLENGE[0])
		self.root.ids.incorrect_challenge.opacity=1
		self.root.ids.incorrect_challenge1.opacity=1
		save()
		Clock.schedule_once(self.correct_challenge1, 1.1)
		

	def correct_challenge1(self,dt):
		self.root.ids.correct_challenge.opacity=0
		self.root.ids.correct_challenge1.opacity=0
		self.root.ids.incorrect_challenge.opacity=0
		self.root.ids.incorrect_challenge1.opacity=0

MainApp().run()
