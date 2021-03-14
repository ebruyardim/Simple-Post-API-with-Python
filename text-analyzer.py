
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import string
from nltk.corpus import stopwords


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/analyze':
            content_length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()

            response = analyze(body)
            self.wfile.write(response)


def analyze(my_data):

    data = json.loads(my_data.decode('utf-8'))
    text = data["text"]
    analysis = []
    try:
        analysis = data["analysis"]
    except KeyError:
        print("There is no 'analysis' list in the json file...")


    english_stopwords = stopwords.words("english")
    turkish_stopwords = stopwords.words("turkish")

    # ***** word count *****
    wordCount = text.count(' ')+1

    # ***** number of letters *****
    numberOfLetter = 0
    for i in text:
        if i in list(string.ascii_letters):
            numberOfLetter += 1

    word_list = text.split()

    word_dict = {word_list[0]:0}

    # removing punctuation marks and adding words to dictionary to count repitations
    for word in word_list:
        for letter in word:
            if letter not in list(string.ascii_letters):
                word = word.replace(letter,'')
        if word in word_dict.keys():
            word_dict[word] += 1
        else:
            word_dict[word] = 1

    longestWord = []
    longest_word_len = 0
    length_of_words = []

    # ***** Guess the text language *****
    number_of_eng_words = 0
    number_of_turk_words = 0
    for word in word_dict:
        if word in english_stopwords:
            number_of_eng_words+=1
        elif word in turkish_stopwords:
            number_of_turk_words+=1

        # ***** finding longest word *****
        word_length = len(word)
        length_of_words.append(word_length)
        if word_length > longest_word_len:
            longest_word_len = word_length
            longestWord.clear()
            longestWord.append(word)
        elif word_length == longest_word_len:
            longestWord.append(word)

    lang = "English" if number_of_eng_words > number_of_turk_words else "Turkish"

    # ***** average length of words *****
    avg_len = sum(length_of_words)/len(length_of_words)
    avg_len = "{:.2f}".format(avg_len)

    # ***** Reading Duration in Seconds *****
    avg_wpm = 250  # average word per minute
    word_per_second = avg_wpm/60
    duration = wordCount*word_per_second
    duration = "{:.2f}".format(duration)
    # ***** median word length *****
    length_of_words.sort()
    medianWordLength = length_of_words[int(wordCount/2)]

    # ***** median word when sorted by length *****
    medianWord = []
    for w in word_list:
        if len(w) == medianWordLength:
            medianWord.append(w)

    # ***** most common 5 words *****
    data_sorted = {k: v for k, v in sorted(word_dict.items(), key=lambda x: x[1])}
    mostCommonWords = list(data_sorted.keys())[-6:-1]
    mostCommonWords.reverse()

    final_dict = {
        "wordCount": wordCount,
        "letters": numberOfLetter,
        "longest": longestWord,
        "avgLength": avg_len,
        "duration": duration,
        "medianWordLength": medianWordLength,
        "medianWord": medianWord,
        "mostCommonWords": mostCommonWords,
        "language":lang
    }
    if len(analysis) != 0:
        for i in list(final_dict.keys()):
            if i not in analysis:
                final_dict.pop(i)

    response = json.dumps(final_dict, indent=2).encode('utf-8')

    return response


httpd = HTTPServer(("localhost",8080), SimpleHTTPRequestHandler)
httpd.serve_forever()

