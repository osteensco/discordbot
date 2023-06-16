import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import nltk
nltk.download('punkt')
nltk.download('wordnet')
import pickle
import time
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from keras.optimizers import SGD






class AIChat():
    def __init__(self) -> None:
        self.stemmer = LancasterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        with open('intents.json') as file:
            self.training_data = json.load(file)

        self.training_in_progress = False
        self.ignore = ['?', '.', '!', ',']
        self.load()




    def clean_words(self, dirty_words):
        cleaned_words = [w.lower() for w in dirty_words if w not in self.ignore]
        cleaned_words = [self.stemmer.stem(w) for w in cleaned_words if w not in self.ignore]
        cleaned_words = [self.lemmatizer.lemmatize(w) for w in cleaned_words if w not in self.ignore]

        return cleaned_words


    def preprocess_training_data(self):
        self.words = []
        self.classes = []
        self.documents = []
        self.model = None

        for intent in self.training_data['intents']:#looks at intent dataset
            for pattern in intent['patterns']:#for each pattern
                #tokenize words to derive meaning
                w = nltk.word_tokenize(pattern)
                self.words.extend(w)
                # add the pattern and its associated class to the documents list
                self.documents.append((w, intent['tag']))
                # add the class to the classes list
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])
                
        # stem, lemmatize and lower each word, and remove duplicates
        self.words = self.clean_words(self.words)
        self.words = sorted(list(set(self.words)))

        # sort classes alphabetically
        self.classes = sorted(list(set(self.classes)))

        pickle.dump(self.words, open('words.pkl', 'wb'))
        pickle.dump(self.classes, open('classes.pkl', 'wb'))
        pickle.dump(self.documents, open('documents.pkl', 'wb'))


    def find_training_set(self):
        try:
            for attr in [self.words, self.classes, self.documents]:
                continue
        except AttributeError:
            try:
                self.words = pickle.load(open('words.pkl', 'rb'))
                self.classes = pickle.load(open('classes.pkl', 'rb'))
                self.documents = pickle.load(open('documents.pkl', 'rb'))
            except FileNotFoundError:
                self.preprocess_training_data()
        

    def train_model(self):
        self.training_in_progress = True
        self.find_training_set()

        # Create training data
        training = []
        output_empty = [0] * len(self.classes)

        for doc in self.documents:
            bag = []
            pattern_words = doc[0]
            pattern_words = self.clean_words(pattern_words)

            for word in self.words:
                bag.append(1) if word in pattern_words else bag.append(0)

            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1

            training.append([bag, output_row])

        random.shuffle(training)
        # print(training)
        # training = np.array(training)

        train_x = np.array([item[0] for item in training])
        train_y = np.array([item[1] for item in training])


        # Build neural network
        self.model = Sequential()
        self.model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(len(train_y[0]), activation='softmax'))

        # Compile model
        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        self.model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
        # Train model
        self.model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
        # Save model
        self.model.save('chatbot_model.h5')

        self.training_in_progress = False


    def load(self):
        try:
            self.find_training_set()
            self.model = load_model('chatbot_model.h5')
        except FileNotFoundError:
            self.train_model()


    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = self.clean_words(sentence_words)
        return sentence_words

    # bag of words is passed to the model to generate predictions
    def bag_of_words(self, sentence, words):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(words)
        for w in sentence_words:
            for i, word in enumerate(words):
                if word == w:
                    bag[i] = 1
        return np.array(bag).flatten()


    def chat(self, msg):
        bag = self.bag_of_words(msg, self.words)
        bag = np.array(bag).reshape((1, 62))
        results = self.model.predict(bag)#returns list of a list [[n1, n2, n3, n4]]
        results_index = np.argmax(results)#returns index of where max value is located
        intent_tag = self.classes[results_index]#match the most likely value to our tag

        if max(results[0]) > 0.90:
            for i in self.training_data["intents"]:
                if i['tag'] == intent_tag:
                    responses = i['responses']

            return random.choice(responses)
            #this could also return other actions, API calls, etc
        
        else:
            return "Not sure how to respond to that"


if __name__ == '__main__':
    bot = AIChat()
    # bot.train_model()
    response = bot.chat('do you age')
    print(response)

