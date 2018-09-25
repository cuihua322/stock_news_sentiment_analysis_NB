# stock_news_sentiment_analysis_NB
Use NLP(nltk.NaiveBayesClassifier) to analysis stock news sentiment 

 ## Website
demo:http://ec2-54-212-23-117.us-west-2.compute.amazonaws.com/stock.php

## Methodology
1. Training Data Collection and Preprocessing

	1.1 crawl stock one month news from https://www.nasdaq.com/symbol/msft/news-headlines for 10 stocks  
	1.2 crawl prices using urllib
  
2. Feature Selection:
	
	tokenize -> remove punctuations & stop words & words which contains number & word frequency < 3
	total feature is  16622  

3. Classification
	
	using nltk.NaiveBayesClassifie as classifier
	training set count: 3000
	test count:892
	accuracy:0.816


## Requirement

Python 3

NLTK

## Usage
### 1.Data Collection

