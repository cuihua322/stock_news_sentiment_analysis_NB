import sys
import nltk
import re
import time
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import pickle
from nltk.stem import WordNetLemmatizer

def process_raw_news(infile):
    file = open(infile, 'r')
    feature_file = open("./input/features_list", 'w')
    train_file = open("./input/train_naiveBayes.data", 'w')
    lmtzr = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    all_words = {}


    while True:
        line = file.readline()
        if not line:
            break
        items = line.split("\t")
        print(len(items))
        if len(items) != 6 or items[3] == "NULL" or items[2] == "NULL":
            continue
        text = items[4]+" "+items[5]
        
        price_change = (float(items[3])-float(items[2]))/float(items[2])
        tag = "neu"
        if price_change > 0.003:
            tag = "pos"
        if price_change < -0.01:
            tag = "neg"

        tokens = nltk.word_tokenize(text)
        outstr = ""
        for word in tokens:
            word = word.lower().strip()
            if is_number(word):
                continue
            word = lmtzr.lemmatize(word)
            if word not in stop_words:
                if word in all_words:
                    all_words[word] += 1
                else:
                    all_words[word] = 1
            outstr += word
            outstr += " "
        train_file.write(tag+"\t"+outstr+"\n")


    for word in all_words.keys():
        if re.match("^[a-z]+$", word) and all_words[word] > 3 and len(word)>1:
            feature_file.write(word+"\n");

    feature_file.close()
    file.close()
    train_file.close()

    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def train_model():
    feature_list = []
    f = open("./input/features_list",'r')
    index = 0
    for line in open("./input/features_list",'r'):
        line = f.readline()
        feature_list.append(line.strip())
    f.close()

    feature_vectors = []
    feature_vectors_nltk = []
    targets = []
    f = open("./input/train_naiveBayes.data")
    count= 0
    for line in open("./input/train_naiveBayes.data"):
        line = f.readline()
        items = line.split("\t")
        tag = items[0]
        targets.append(tag)
        tokens = nltk.word_tokenize(items[1])
        words = set()
        for word in tokens:
            words.add(word)
        feature_vector = []
        feature_vector_nltk = {}
        for word in feature_list:
            if word not in words:
                feature_vector.append(0)
                feature_vector_nltk[word] = False
            else:
                feature_vector.append(1)
                feature_vector_nltk[word] = True
        feature_vectors.append(feature_vector)
        feature_vectors_nltk.append((feature_vector_nltk,tag))
        print(count)
        count += 1
    train = feature_vectors_nltk[:3000]
    test = feature_vectors_nltk[3000:]
    classifier = nltk.NaiveBayesClassifier.train(feature_vectors_nltk)
    totalcount = 0
    same = 0
    diff = 0
    for item in test:
        predic = classifier.classify(item[0])
        print(predic+" "+item[1])
        if predic == item[1]:
            same += 1
        else:
            diff += 1
        totalcount += 1
    f.close()
    print(same/totalcount)
    filename = './data/model_nb.sav'
    pickle.dump(classifier, open(filename, 'wb'))

'''    X_train, X_test, y_train, y_test = train_test_split(feature_vectors, targets, test_size=0.33, random_state=42)
    print(y_train)
    negcount = 0
    poscount = 0
    neucount = 0
    for tag in y_train:
        if tag == "neg":
            negcount += 1
        if tag == "pos":
            poscount += 1
        if tag == "neu":
            neucount += 1
    print("neucount:" + str(neucount) + "poscount:" +str(poscount) + "negcount:"+str(negcount))
    #clf = GaussianNB()
    clf = BernoulliNB()
    clf.fit(X_train, y_train);
    
    #clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(5, 2), random_state=1)
    #clf.fit(X_train, y_train)
    print(clf.classes_)
    filename = './data/model_nb.sav'
    pickle.dump(clf, open(filename, 'wb'))
    y_pred = clf.predict(X_test)
    print(y_pred)
    print(y_test)
    print(accuracy_score(y_test, y_pred))
    '''

def setiment_predict(newsfile, result):
    feature_list = []
    infile = open("./input/features_list",'r')
    outfile = open(result,'w')
    for line in open("./input/features_list",'r'):
        line = infile.readline()
        feature_list.append(line.strip())
    infile.close()
    print(len(feature_list))
    infile = open(newsfile)
    lmtzr = WordNetLemmatizer()
    feature_vectors = []
    classifier = pickle.load(open('./data/model_nb.sav', 'rb'))
    for line in open(newsfile):
        line = infile.readline()
        items = line.split("\t")
        if len(items) != 7 :
            continue
        text = (items[4]+" "+items[6]).strip().lower()
        print(text)
        tokens = nltk.word_tokenize(text)
        words = set()
        for i in range(len(tokens)):
            words.add(lmtzr.lemmatize(tokens[i]))
        feature_vector = {}
        for word in feature_list:
            if word in words:
                feature_vector[word] = True
            else:
                feature_vector[word] = False
        dist = classifier.prob_classify(feature_vector)
        maxlable = classifier.classify(feature_vector)
        label_pro_str = ""
        for label in dist.samples():
            label_pro_str += " "+ label+":"+str(dist.prob(label))
        outfile.write(items[0]+"\t"+items[4]+"\t"+items[5]+"\t"+maxlable+"\t"+label_pro_str.strip()+"\n")
    infile.close()
    outfile.close()



if __name__ == "__main__":
    if sys.argv[1] == '-train':
        process_raw_news("./data/history_news.data")
        train_model()
    if sys.argv[1] == '-predict':
        today_date = time.strftime('%Y%m%d',time.localtime(time.time()))
        infile = './data/News/'+today_date+'_news'
        outfile = './data/Out/'+today_date+'_out'
        today_date = "20180924"
        setiment_predict(infile, outfile)
