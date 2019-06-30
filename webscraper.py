import json
from lxml import html
from re import findall
import math
import pickle
from pathlib import Path
import nltk
from nltk.corpus import stopwords
#nltk.download


class InvertedIndex:
    def __init__(self):
        self.folder_paths = []  # list of paths to each file (ex. 3/21)
        self.inverted_index = {}    # key = word, value = [path, tf]
        self.dictjson = {}  # dictionary with path keys and URL values

    def parse_json(self):
        '''parses the bookkeeping.json file, saves it as a dictionary,
        and saves a list of the paths'''
        with open("bookkeeping.json", 'r') as f:
            json_data = json.load(f)
            self.dictjson = json_data

        for path in json_data:
            self.folder_paths.append(path)

    def extract_content(self):
        '''reads each file in WEBPAGES_RAW, extracts, tokenizes, and adds the content
        to the inverted index'''
        for path in self.folder_paths:
            with open(path, encoding = 'utf-8') as p:
                read_file = p.read()
                if read_file != "":
                    try:
                        doc = html.fromstring(read_file)    # fixes broken html

                        # lists of the scraped content from tags
                        scraped_head = doc.xpath('//head/text()')
                        scraped_body = doc.xpath('//body/text()')
                        scraped_title = doc.xpath('//title/text()')
                        scraped_h1 = doc.xpath('//h1/text()')
                        scraped_h2 = doc.xpath('//h2/text()')
                        scraped_h3 = doc.xpath('//h3/text()')
                        scraped_b = doc.xpath('//b/text()')
                        scraped_strong = doc.xpath('//strong/text()')
                        scraped_address = doc.xpath('//address/text()')
                        scraped_p = doc.xpath('//p/text()')
                        scraped_div = doc.xpath('//div/text()')
                        scraped_a = doc.xpath('//a/text()')

                        # tokenize scraped content and add to inverted index
                        self.tokenize(scraped_head, path)
                        self.tokenize(scraped_body, path)
                        self.tokenize(scraped_title, path)
                        self.tokenize(scraped_h1, path)
                        self.tokenize(scraped_h2, path)
                        self.tokenize(scraped_h3, path)
                        self.tokenize(scraped_b, path)
                        self.tokenize(scraped_strong, path)
                        self.tokenize(scraped_address, path)
                        self.tokenize(scraped_p, path)
                        self.tokenize(scraped_div, path)
                        self.tokenize(scraped_a, path)
                        
                    except:
                        continue
                    
    def tokenize(self, L, p):
        '''tokenizes the elements of list L and adds each token to the inverted index'''
        print(p)

        tokens = []
        found = False
        
        for elem in L:
            tokens = findall(r"[a-zA-Z0-9]+", elem.lower()) #list of tokens
            
        for token in tokens:
            print(token)
            if token not in self.inverted_index:
                self.inverted_index[token] = [[p, 1]]
                
            elif token in self.inverted_index:
                for val in self.inverted_index[token]:
                    if val[0] == p: # if path already in token's posting list
                        val[1] += 1     # increment # of appearances in file
                        found = True
                        break
                    
                if found == False:  # if path is not yet in token's posting list, add it
                    self.inverted_index[token].append([p, 1])

                found = False

    def write_to_file(self):
        '''adds tf-idf to inverted index saves it to a file'''
        self.tf_idf()
        with open("newinvertedindex.txt", 'wb') as file:
            pickle.dump(self.inverted_index, file)
            file.close()

    def tf_idf(self):
        '''update postings with tf-idf'''
        num_doc = float(len(self.folder_paths))
        
        for word in self.inverted_index:
            df = len(self.inverted_index[word])  # doc freq is the length of posting list
            idf = math.log10(num_doc/float(df))    # idf is log (N/df)
                       
            for posting_index in range(df):
                tf = self.inverted_index[word][posting_index][1]
                tfidf = (1 + math.log10(tf)) * idf
                self.inverted_index[word][posting_index][1] = tfidf # change tf of postings to tf-idf
            
    def cosine_similarity(self, wordlist, i):
        num_doc = float(len(self.folder_paths))
        scores = {}
        lengths = {}
        for word in wordlist:
            tf_query = wordlist.count(word)
            idf_query = math.log10(num_doc/float(len(i[word])))
            tfidf_query = (1 + math.log10(tf_query)) * idf_query

            for posting in i[word]:
                if posting[0] not in scores:
                    scores[posting[0]] = tfidf_query * posting[1]
                elif posting[0] in scores:
                    scores[posting[0]] += tfidf_query * posting[1]
                if posting[0] not in lengths:
                    lengths[posting[0]] = (tfidf_query**2)
                elif posting[0] not in lengths:
                    lengths[posting[0]] += (tfidf_query**2)
                
        # normalize weights
        for path in scores:
            scores[path] = float(scores[path]) / float(math.sqrt(lengths[posting[0]]))

        sorted_scores = sorted(scores.items(), key = lambda x: x[1], reverse = True)
 #       print(sorted_scores)
        return sorted_scores
    
    def query(self, word, i):
        '''returns a string with the top 20 search result webpages for the query'''
        url_string = ""
        #all_paths = {}
        num_doc = len(self.folder_paths)
 #       nltk.downloads('stopwords')
        stop_list = set(stopwords.words('english'))
        
        # if query is empty
        if word == "":
            return
        
        word = word.lower() # lowercase query to index inverted index
        wordlist = word.split() #list of all words in input
 #       wordlistlength = len(wordlist)
 #       print(stop_list)
        #If a word in the query is a stopword, remove it from query
        for Word in wordlist:
            if Word in stop_list:
                wordlist.remove(Word)
 #       print(wordlist)
        wordlistlength = len(wordlist)

                
        #if query has more than one word
        if wordlistlength > 1:
            try:
                sorted_scores = self.cosine_similarity(wordlist,i)
                for path, score in sorted_scores[:20]:
                    url_string += str(self.dictjson[path]) + "\n\n"

            except KeyError:
                return "No results found!"

        # if query is a single word
        
        else: 
            #counter = 0
            try:
                rankings = {}
                for val in i[wordlist[0]]:
                    print("VAL[0]:", val[0])
                    print("VAL[1]:", val[1])
                    rankings[val[0]] = val[1]
                    #counter += val[1]
                #print("Total HITS : " + str(counter) + "\n")
                    
                sorted_rankings = sorted(rankings.items(), key = lambda x: x[1], reverse = True)
                print(sorted_rankings)        
                for path, tfidf in sorted_rankings[:20]:
                    url_string += str(self.dictjson[path]) + "\n\n"
                    
            except KeyError:
                return "No results found!"
                
        return url_string

#if __name__ == '__main__':
#    ii = InvertedIndex()
#    ii.parse_json()
#    my_file = Path("newinvertedindex.txt")
#    
#    if not my_file.is_file():
#        ii.extract_content()
#        ii.write_to_file()
#    ii.query()
