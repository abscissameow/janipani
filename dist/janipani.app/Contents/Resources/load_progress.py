import pickle
from wanikani import *

#insert full path to your current DATA.pkl file to transfer progress
source = '???'
with open(source, 'rb') as inp:
    DATA_prev=pickle.load(inp)

with open('DATA.pkl', 'rb') as inp:
    DATA=pickle.load(inp)

for i in range(60):
    for j in range(len(DATA[i]['rad'])):
        DATA[i]['rad'][j].stage=DATA_prev[i]['rad'][j].stage
        DATA[i]['rad'][j].previous_review=DATA_prev[i]['rad'][j].previous_review
    for j in range(len(DATA[i]['kan'])):
        DATA[i]['kan'][j].stage=DATA_prev[i]['kan'][j].stage
        DATA[i]['kan'][j].previous_review=DATA_prev[i]['kan'][j].previous_review
    for j in range(len(DATA[i]['voc'])):
        DATA[i]['voc'][j].stage=DATA_prev[i]['voc'][j].stage
        DATA[i]['voc'][j].previous_review=DATA_prev[i]['voc'][j].previous_review

with open('DATA.pkl', 'wb') as outp:
    pickle.dump(DATA, outp, pickle.HIGHEST_PROTOCOL)