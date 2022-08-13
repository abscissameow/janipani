おはいよう!
this is the free copy of wanikani for mac users

-----HOW TO INSTALL:

download janipani.app
* if you face problems with opening (administration rights) then 
* run this commands in terminal (replace /path/to/app with your actual path to app):
    sudo xattr -dr com.apple.quarantine /path/to/app
    chmod -R 755 /path/to/app

-----HOW TO USE:

1) learn meanings and readings of hyerogliphs in LESSONS tab (press cake button if you done with one)
2) make review of your learned hyerogliphes in REVIEWS:\
    *you can check the stage of the hyerogliph in rectangular button, tap it to see the time since last preview\
    *if you mad a mistake just click the textfield and ENTER\
    *if you want to recall the info about the hyerogliph tap the book button\
    *if you mad a typo then tap the shield button and try again
3) you can check statistics in INFO tab, the search textfield can be used as follows:\
    a) '3 voc to remove' (aka 'lvl type meaning', where 1<lvl<60, type is one of rad/kan/voc, meaning is one of meanings of hyerogliph)\
    b) 'to be born' (u can search for any meaning and u will get all possible hyerogliphs)\
    c) '3 kan' (aka 'lvl type' to see all hyerogliphs of the type for the lvl) or just 'lvl 3'
    d) 'check 10' (aka 'check n' to see the hyerogliphs that soon be reviewed)\
    _e) '_stage 3 voc end 4' (aka '_stage lvl type meaning stage' to adjust hye's stage to preferred one)\
    _f) '_time 3 voc to be born' (aka '_time lvl type meaning' to decrease last review time by 1000 hours)\
    *you can check the stage of the hyerogliph in rectangular button, tap it to see the residual time to review, tap it again to see the time since last preview\
    _g) '_spread 10' (aka 'spread n' to increase time of last review for each hyerogliph for random value of hours between 0 and n)

p.s. if u want to load existing progress from your DATA.pkl use fit.ipynb or load_progress.py\
p.p.s. for last updates just replace your janipani.app/Contents/Resources/janipani.py file with the janipani.py from github
