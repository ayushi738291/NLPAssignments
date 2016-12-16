import nltk
import nltk.chunk
import codecs
import viterbi
from collections import Counter
from sklearn.metrics import confusion_matrix
def load_sentences(path):
    sentences = []
    sentence = []
    for line in codecs.open(path, 'r', 'utf8'):
        line = line.rstrip()
        if not line:
            if len(sentence) > 0:
                if 'DOCSTART' not in sentence[0][0]:
                    sentences.append(sentence)
                sentence = []
        else:
            word = line.split()
            assert len(word) >= 2
            sentence.append(word)
    if len(sentence) > 0:
        if 'DOCSTART' not in sentence[0][0]:
            sentences.append(sentence)
    return sentences

#print(conll2000.sents())

train='./dataset/conll2000/train.txt'
allData=load_sentences(train)
globalData=[]
for i in allData:
    for j in i:
        globalData.append(j)

globalData=[tuple(l) for l in globalData]

freq_word=nltk.FreqDist(word for (word,tag,chunck) in globalData)
freq_tag=nltk.FreqDist(tag for (word,tag,chunck) in globalData)
freq_chunck=nltk.FreqDist(chunck for (word,tag,chunck) in globalData)  

allbigrams=list(nltk.bigrams(globalData))

#all unique words,tags,chuncks
allWords=[a for a in freq_word]
allTags=[a for a in freq_tag]
allChunk=[a for a in freq_chunck]


dict1={}
#P(chunk_i|chunk_i-1)
for i in allChunk:
    ne_type=[b[2] for (a,b) in allbigrams if a[2]==i]
    dict1[i]=ne_type
for i in dict1 :
    dict1[i]=dict(Counter(dict1[i]))
    totalCount=sum(dict1[i].values());
    for k in dict1[i]:
        dict1[i][k]/=float(totalCount)
    #print (i, ':', dict1[i])
   
print('--------aa---------')
#P(tag_i|tag_i-1)
dict2={}
for i in allTags:
    ne_type=[b[1] for (a,b) in allbigrams if a[1]==i]
    dict2[i]=ne_type
for i in dict2 :
    dict2[i]=dict(Counter(dict2[i]))
    totalCount=sum(dict2[i].values());
    for k in dict2[i]:
        dict2[i][k]/=float(totalCount)

print('--------bb---------')
#P(tag_i|chunk_i)
dict4={}
for i in allChunk: # i:word x:chunk y:tag
    dict4[i]=[x for (a,x,j) in globalData if j==i]
count=0
for i in dict4 :
    dict4[i]=dict(Counter(dict4[i]))
    totalCount=sum(dict4[i].values());
    for k in dict4[i]:
        dict4[i][k]/=float(totalCount)

print('--------cc---------')
#P(W_i|tag_i)
dict3={}
for i in allTags: # i:word y:tag
    dict3[i]=[a for (a,x,j) in globalData if x==i]
for i in dict3 :
    dict3[i]=dict(Counter(dict3[i]))
    totalCount=sum(dict3[i].values());
    for k in dict3[i]:
        dict3[i][k]/=float(totalCount)
print('--------dd---------')

#Probability of tags being starting tag
sentencestart = dict(zip(allTags,[1 for x in range(0,len(allTags))]))

for i in allData:
    if i[0][1] in sentencestart.keys():
        sentencestart[i[0][1]]+=1
    else:
        sentencestart[i[0][1]]=1
#totalCount=len(allWords)
totalCount=sum(sentencestart.values())
for i in sentencestart:
    sentencestart[i]/=float(totalCount)

#Probability of chunk being starting chunk
startchunk=dict(zip(allChunk,[1 for x in range(0,len(allChunk))]))
for i in allData:
    if i[0][2] in startchunk.keys():
        startchunk[i[0][2]]+=1
    else:
        startchunk[i[0][2]]=1
totalCount=sum(startchunk.values())
for i in startchunk:
    startchunk[i]/=float(totalCount)

print('--------ff---------')    
print('-------------------')
print("-----testing-------")
test='./dataset/conll2000/test_lesser.txt'
allTestData=load_sentences(test)

count=0
predicted_tag=[]
predicted_chunk=[]
for i in allTestData:
    sent=[]    
    for j in i:
        j[0]=j[0].encode('utf8')
        sent+=[j[0]]
    #print(sent)d
    param={}
    
    param['states'] = tuple(allTags) 
    param['observations'] = tuple(sent) 
    param['start_probability'] = sentencestart 
    param['transition_probability'] = dict2
    param['emission_probability'] = dict3
    obj= viterbi.Viterbi(param)   
    x=obj.viterbi()[1]
    predicted_tag=predicted_tag+[x]

    param1={}
    
    param1['states'] = tuple(allChunk) 
    param1['observations'] = tuple(x) 
    param1['start_probability'] = startchunk 
    param1['transition_probability'] = dict1
    param1['emission_probability'] = dict4

    obj= viterbi.Viterbi(param1)   
    predicted_chunk=predicted_chunk+[obj.viterbi()[1]]

    count+=1
   	
#obj.efficiency()        
actual=[]
for i in allTestData:
    line=[]
    for j in i:
        line=line+[j[2]]
    actual=actual+[line]    
x=0;
correct=0;total=0
for i in actual:
    y=0;
    for j in i:
        if(j==predicted_chunk[x][y]):
            correct+=1;
        total+=1
        y+=1
    x+=1

accuracy=((correct+0.0)/total)*100
#predicted_label=[item for sublist in predicted_chunk for item in sublist]
#actual_label=[item for sublist in actual for item in sublist]
#cn=confusion_matrix(actual_label,predicted_label,labels=allChunk);
print (accuracy)
