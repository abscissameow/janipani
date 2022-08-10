from kivy.lang import Builder
from kivymd.app import MDApp
from wanikani import *
import pickle, random

def save():
	# return
	with open('DATA.pkl', 'wb') as outp:
		pickle.dump(DATA, outp, pickle.HIGHEST_PROTOCOL)

with open('DATA.pkl', 'rb') as inp:
    DATA=pickle.load(inp)

# def reset():
# 	for i in range(60):
# 		for j in DATA[i].values():
# 			for k in j:
# 				k.previous_review-=3600*24*60
# 				k.stage=-1
# 	save()
# #reset()

def is_it(input, answers, indicator):
	if indicator:
		return input in answers
		
	def compare(inp_word,true_word):
		mistakes=0
		dictrue,dicinp = {},{}
		for i in true_word:
			if i in dictrue: 
				dictrue[i] += 1
			else: 
				dictrue[i] = 1
		for i in inp_word:
			if i in dicinp: 
				dicinp[i] += 1
			else: 
				dicinp[i] = 1
		for i in dictrue:
			if i not in dicinp:
				if i>='0' and i<='9':
					return 10
				mistakes+=dictrue[i]
				continue
			mistakes+=abs(dictrue[i]-dicinp[i])
		for i in dicinp:
			if i not in dictrue:
				if i>='0' and i<='9':
					return 10
				mistakes+=dicinp[i]
				continue
			mistakes+=abs(dictrue[i]-dicinp[i])
		return mistakes
    
	# res=True
	# input_words=input.split(' ')
	# same_length=0
	# mistakes=0
	for phrase in answers:
		if compare(input,phrase)<=(1 if len(phrase)<=5 else 2):
			return True
		# phrase_words=phrase.split(' ')
		# if len(input_words)!=len(phrase_words):
		# 	continue
		# else:
		# 	mistakes=0
		# 	same_length=1
		# for i in range(len(phrase_words)):
		# 	mistakes += compare(input_words[i],phrase_words[i])

		# if mistakes<=len(phrase_words):
		# 	return True
	return False
	# if mistakes>len(phrase_words):
	# 		return False

	# return (res if same_length else False)

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
	L,voc_check=[],0
	for radical in DATA[lvl-1]['rad']:
		if radical.stage==-1:
			L.append(radical)
	if not L:
		voc_check=1
		for kanji in DATA[lvl-1]['kan']:
			if kanji.stage<3:
				voc_check=0
				if kanji.stage==-1:
					L.append(kanji)
	if voc_check:
		for vocab in DATA[lvl-1]['voc']:
			if vocab.stage==-1:
				L.append(vocab)
	return L

def Lvl():
	lvl=1
	for lv in range(59):
		if sum([1 if i.stage>4 else 0 for i in DATA[lv]['kan']])>=len(DATA[lv]['kan'])*0.9 or sum([1 if i.stage>0 else 0 for i in DATA[lv+1]['kan']]):
			lvl+=1
		else:
			return lvl
	if sum([1 if i.stage>4 else 0 for i in DATA[59]['kan']])>=len(DATA[59]['kan'])*0.9:
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
			self.root.ids.play_lesson.text=f'{len(list_lessons(DATA,self.lvl))} CAKES!'
		self.theme_cls.primary_palette = "Pink"
		self.theme_cls.primary_hue='200'
	def press_review_tab(self):
		if not self.reviews:
			self.root.ids.play_review.text=f'{len(list_reviews(DATA,self.lvl,self.reviews))+len(self.reviews)} CAKES!' 
		self.theme_cls.primary_palette = "Cyan"
		self.theme_cls.primary_hue='500'
	def press_info_tab(self):
		self.root.ids.Apprentice.text,self.root.ids.Guru.text,self.root.ids.Master.text,self.root.ids.Enlightened.text,self.root.ids.Burned.text=count_stages(self.lvl)
		loc=sum([1 if i.stage>4 else 0 for i in DATA[self.lvl-1]['kan']])
		self.root.ids.progress.text=f'Your level is {self.lvl}'
		self.root.ids.progress_bar.value=100*loc/len(DATA[self.lvl-1]['kan'])
		self.root.ids.search.current_hint_text_color=self.theme_cls.primary_color
		self.root.ids.search.hint_text="   search: 'rad/kan/voc meaning'"
		self.root.ids.active_lessons.text = f'Active lessons: {len(list_lessons(DATA,self.lvl))}'
		self.root.ids.active_reviews.text = f'Active reviews: {len(self.reviews)+len(list_reviews(DATA,self.lvl,self.reviews))}'
		self.theme_cls.primary_palette = "DeepPurple"
		self.theme_cls.primary_hue='300'
	
	def hide_everything_lesson(self):
		self.root.ids.play_lesson.text=''
		self.root.ids.next_lesson_button.opacity=0
		self.root.ids.next_lesson_button.disabled=True
		self.root.ids.next_lesson.text=''
		self.root.ids.accordion.opacity=0
		self.root.ids.info_mdcard.opacity=0
		self.root.ids.mdcard_lesson.opacity=0
		self.root.ids.play_lesson_button.opacity=0
		self.root.ids.play_lesson_button.disabled=True

	def press_lesson_cake(self):
		self.lessons=list_lessons(DATA,self.lvl)
		if not self.lessons:
			self.hide_everything_lesson()
			self.root.ids.play_lesson.text='SORRY NO CAKES!'
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
		self.root.ids.mdcard_lesson.md_bg_color=colors[hye.type]
		if hye.type=='rad':
			self.root.ids.meaning.text = "Meaning: "+hye.meaning
			self.root.ids.kun_reading.text=''
			self.root.ids.on_reading.text=''
			self.root.ids.mnemonics_meaning.text=hye.mnemonics
			self.root.ids.mnemonics_meaning_ru.text=hye.mnemonics_ru
			self.root.ids.mnemonics_reading.text="YOU MUST LISTEN TO ME, THIS IS VERY IMPORTANT!"
			self.root.ids.mnemonics_reading_ru.text="THE MOST IMPORTANT THING YOU MUST DO IS ..."
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
			self.root.ids.on_reading.font_size=self.root.ids.kun_reading.font_size*0.8
			self.root.ids.on_reading.text="Example: "+hye.context_sents[0]+f'\n({hye.context_sents[1]})'
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

	def press_review_cake(self):
		self.root.ids.refresh_button.icon='refresh'
		self.root.ids.input.error=False
		new_reviews=list_reviews(DATA,self.lvl,self.reviews)
		self.reviews+=new_reviews
		self.reviews_pack=self.reviews[:self.pack_size]
		random.shuffle(self.reviews_pack)
		
		self.hide_everything_review()
		
		if not self.reviews:
			self.root.ids.play_review.text='SORRY NO CAKES!'
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
		
		self.root.ids.meaning_reading.text=randdict[self.rand].capitalize()
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
			exec('self.hye_review.ind_'+randdict[self.rand]+'=1')
			
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
			if sum([1 if i.stage>4 else 0 for i in DATA[self.lvl-1]['kan']])==len(DATA[self.lvl-1]['kan']):
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
				return
			
			if (self.root.ids.input.text.lower() in n) or (convert_(self.root.ids.input.text.lower(),not self.rand) in n):
				self.root.ids.meaning_reading.text = f"oops! I am looking for {randdict[self.rand].capitalize()}!"
				return
			self.root.ids.input.error_color= (1, 0, 0, 1)
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
			self.root.ids.input.helper_text='sumimasen!<3'
			self.root.ids.input.error_color= (0, 1, 0, 1)
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
		self.root.ids.mdcard_lesson_review.md_bg_color=colors[hye.type]
		if hye.type=='rad':
			self.root.ids.meaning_review.text = "Meaning: "+hye.meaning
			self.root.ids.kun_reading_review.text=''
			self.root.ids.on_reading_review.text=''
			self.root.ids.mnemonics_meaning_review.text=hye.mnemonics
			self.root.ids.mnemonics_meaning_ru_review.text=hye.mnemonics_ru
			self.root.ids.mnemonics_reading_review.text="YOU MUST LISTEN TO ME, THIS IS VERY IMPORTANT!"
			self.root.ids.mnemonics_reading_ru_review.text="THE MOST IMPORTANT THING YOU MUST DO IS ..."
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
			self.root.ids.on_reading_review.font_size=self.root.ids.kun_reading.font_size*0.8
			self.root.ids.on_reading_review.text="Example: "+hye.context_sents[0]+f'\n({hye.context_sents[1]})'
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
		
		self.root.ids.info_next.opacity=0
		self.root.ids.info_next.disabled=True
		self.root.ids.next_lesson_button_info.opacity=0
		self.root.ids.next_lesson_button_info.disabled=True
		self.root.ids.next_lesson_info.text=''
		self.root.ids.accordion_info.opacity=0
		self.root.ids.info_mdcard_info.opacity=0
		self.root.ids.mdcard_lesson_info.opacity=0
	
	def press_lesson_cake_info(self):
		self.hide_everything_info()
		self.root.ids.progress.opacity=1
		loc=sum([1 if i.stage>4 else 0 for i in DATA[self.lvl-1]['kan']])
		self.root.ids.progress.text=f'Your level is {self.lvl}'
		self.root.ids.progress_under.text='guru kanji '+str(loc)+'/'+str(len(DATA[self.lvl-1]['kan']))
		self.root.ids.progress_bar.value=100*loc/(len(DATA[self.lvl-1]['kan'])*0.9)
		self.root.ids.progress_bar.opacity=1
		self.root.ids.search.current_hint_text_color=self.theme_cls.primary_color
		self.root.ids.search.hint_text="   search: 'rad/kan/voc meaning'"
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
				self.infos=[]
				L=self.root.ids.search.text.lower().split(' ',1)
				if L[0]=='_stage':
					lvl,typ,h,to=L[1].split(' ')
					for i in DATA[int(lvl)-1][typ]:
						if h in i.meaning:
							i.stage=int(to)
							save()
							self.root.ids.search.text+=' done'
							return
				elif L[0]=='_time':
					lvl,typ,h=L[1].split(' ')
					for i in DATA[int(lvl)-1][typ]:
						if h in i.meaning:
							i.previous_review=time.time()-1000*3600
							save()
							self.root.ids.search.text+=' done'
							return
				elif L[0]=='lvl':
					self.infos=[item for sublist in DATA[int(L[1])-1].values() for item in sublist]
				elif L[0]=='check' and len(L)>1:
					maxl=int(L[1])
					for i in range(self.lvl):
						for hyes in DATA[i].values():
							for k in hyes:
								if len(self.infos)<maxl:
									self.infos.append(k)
								else:
									for j in range(maxl):
										if (k not in self.infos) and k.previous_review>self.infos[j].previous_review:
											self.infos[j]=k
				elif L[0] not in ['rad','kan','voc']:
					for i in range(60):
						for hyes in DATA[i].values():
							for hye in hyes:
								for meaning in (lambda x: [x] if hye.type=='rad' else x)(hye.meaning):
									if L[0] in meaning:
										self.infos.append(hye)
										break
				else:
					type,text = L
					if text>='1' and text<='60':
						self.infos=[i for i in DATA[int(text)-1][type]]
					else:
						for i in range(60):
							for hye in DATA[i][type]:
								for meaning in (lambda x: [x] if type=='rad' else x)(hye.meaning):
									if text in meaning:
										self.infos.append(hye)
										break
				if not self.infos:
					self.root.ids.search.current_hint_text_color=(1,0.2,0.2,1)
					self.root.ids.search.hint_text=f"   couldn't find relevant: '{self.root.ids.search.text}'"
					self.root.ids.search.text=''
					return
			except:
				self.root.ids.search.current_hint_text_color=(1,0.2,0.2,1)
				self.root.ids.search.hint_text=f"   couldn't find relevant: '{self.root.ids.search.text}'"
				self.root.ids.search.text=''
				return
		else:
			if not self.infos:
				self.press_lesson_cake_info()
				return
		
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
			self.root.ids.mnemonics_reading_info.text="YOU MUST LISTEN TO ME, THIS IS VERY IMPORTANT!"
			self.root.ids.mnemonics_reading_ru_info.text="THE MOST IMPORTANT THING YOU MUST DO IS ..."
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
			self.root.ids.on_reading_info.font_size=self.root.ids.kun_reading.font_size*0.8
			self.root.ids.on_reading_info.text="Example: "+hye.context_sents[0]+f'\n({hye.context_sents[1]})'
			self.root.ids.mnemonics_meaning_info.text=hye.mnemonics_meaning
			self.root.ids.mnemonics_meaning_ru_info.text=hye.mnemonics_meaning_ru
			self.root.ids.mnemonics_reading_info.text=hye.mnemonics_reading
			self.root.ids.mnemonics_reading_ru_info.text=hye.mnemonics_reading_ru
			self.root.ids.hyerogliph_lesson_info.text=hye.hyerogliph
		
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
				self.root.ids.stage_info.text='who knows'
			else:
				self.root.ids.stage_info.text=residual
		elif self.root.ids.stage_info.text in [residual,'who knows']:
			if self.hye_info.stage==-1:
				self.root.ids.stage_info.text='not exists'
			else:
				t=time.time()-self.hye_info.previous_review
				self.root.ids.stage_info.text=str(round(t//(3600*24)))+'d '+ str(round((t-round(t//(3600*24))*3600*24)//3600))+'h'
		else:
			self.root.ids.stage_info.text=stage


		


MainApp().run()






