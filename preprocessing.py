import spacy
from spacy.language import Language
import inflect
import nltk
from nltk.tokenize import word_tokenize
from googletrans import Translator

redundant_list = ['ORG', 'GPE', 'CARDINAL', 'NORP', 'PERCENT', 'WORK_OF_ART', 'LOC', 'QUANTITY', 'FAC', 'EVENT', 'ORDINAL', 'PRODUCT', 'LAW', 'LANGUAGE']

@Language.component("entities_removal")
def entities_removal(doc):
    ents = list(doc.ents)
    for ent in ents[:]:
        if ent.label_ in redundant_list:
            ents.remove(ent)
    ents = tuple(ents)
    doc.ents = ents
    return (doc)
Language.component("entities_removal", func=entities_removal)

def singular(inp):
    pts = inflect.engine()
    tokenized = word_tokenize(inp)
    pos = nltk.pos_tag(tokenized)
    sent = ""
    for s in pos:
        if s[1] == 'NNS':
            try:
                sent += pts.singular_noun(s[0]) + " "
            except Exception as e:
                sent += s[0] + " "
        else:
            sent += s[0] + " "
    return sent

def engzh_separation(oo):
    zhwds = ''
    engwds = ''
    zh_pun_flag=False
    eng_pun_flag=False
    zh_hi_flag=False
    eng_hi_flag=False
    for ii, c in enumerate(oo):
        if c.isascii():
            if zh_pun_flag==True and zh_hi_flag==True and c=='$':    # -$
                zhwds += c
                zh_hi_flag = False
                continue
            elif eng_pun_flag==True and eng_hi_flag==True and c=='$':  # -$
                engwds += c
                eng_hi_flag = False
                continue
            elif c=='$' and not oo[ii-1].isascii() and zh_pun_flag==False:   # and '$'
                zhwds += c
                zh_pun_flag = True
                continue
            elif c=='$' and oo[ii-1].isascii() and eng_pun_flag==False:    # and '$'
                engwds += c
                eng_pun_flag = True
                continue
            elif c.isnumeric() and zh_pun_flag==True:   # $4 <-after dollar sign
                zhwds += c
                zh_pun_flag=False
                continue
            elif c.isnumeric() and eng_pun_flag==True:  # $4 <-after dollar sign
                engwds += c
                eng_pun_flag=False
                continue
            elif c=='-' and not oo[ii-3].isascii():     # -
                zhwds += c
                zh_hi_flag = True
                zh_pun_flag = True
                continue
            elif c=='-' and oo[ii-3].isascii():        # -
                engwds += c
                eng_hi_flag = True
                eng_pun_flag = True
                continue
            elif c.isnumeric() and len(engwds)!=0 and engwds[len(engwds)-1].isnumeric():  # num fol num
                engwds += c
                continue
            elif c.isnumeric() and len(zhwds)!=0 and zhwds[len(zhwds)-1].isnumeric():     # num fol num
                zhwds += c
                continue
            elif c.isnumeric() and oo[ii-1].isascii():  # num 
                engwds += c
                continue
            elif c.isnumeric() and not oo[ii-1].isascii():
                zhwds += c
                continue
            engwds += c
            if ii!=len(oo)-1 and not oo[ii+1].isascii():
                engwds += " "
        else:
            zhwds += c
    return engwds, zhwds

def tw_cn(tt):
    translator = Translator()
    translations = translator.translate([tt], dest='zh-cn')
    for c in translations:
            descrip_zhcn = c.text
    descrip_zhcn = list(descrip_zhcn)
    for i in range(len(descrip_zhcn)):
        if descrip_zhcn[i]=='慨':
            descrip_zhcn[i]='嘅'
    descrip_zhcn = ''.join(descrip_zhcn)
    return descrip_zhcn

def ner_chin(model_path, doc):
    pred_list = []
    nlp = spacy.load(model_path)
    doc = tw_cn(doc)
    pred = nlp(doc)
    for ent in pred.ents:
        word = ent.text.encode('utf-8').decode('utf-8')
        pred_list.append((word, ent.label_))
    return pred_list

def ner_eng(model_path, doc):
    pred_list = []
    nlp = spacy.load(model_path)
    doc = singular(doc.lower())
    pred = nlp(doc)
    for ent in pred.ents:
        pred_list.append((ent.text, ent.label_))
    return pred_list
