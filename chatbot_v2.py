import numpy as np 
from textblob import TextBlob, Word
import random
import re
import logging


LOG_FILENAME = 'chat_text.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.WARNING)
logging.debug('This message should go to the log file')


# Sentences we'll respond with if the user greeted us
Greetings_Keywords = ("hello", "hi", "greetings", "sup", "what's up", "moring", "evening", "afternoon", "hey")
Greetings_Responses = ["Hello! How may I help you.", "What you would like to have.", "Hello :)"]
Default_response = ["Pardon please, what you want? Do you like to have ", "Would you like ", "Sorry , would you like", 
                    "Pardon, may i suggest you a "]

#the menu item and prices can also be fetched from server/a local database or a file locally stored
coffee_list = ["americano", "caffe latte", "cafe mocha", "cappccino", "espresso", "indian filter coffee", "instant coffee"
              , "irish cappccino", "hazelnut cappccino"]
coffee_list_r = ["americano", "caffelatte", "cafemocha", "cappccino", "espresso", "indianfiltercoffee", "instantcoffee"
              , "irishcappccino", "hazelnutcappccino"]
coffee_list_print = "We have\nAmericano\nCaffe Latte\nCafe Mocha\nCappccino\nEspresso\nIndian Filter" +\
"Coffee\nInstant Coffee\nIrish Cappccino\nHazelnut Cappccino\nWhat would you like to have?"
price_coffee = ["120", "125", "120", "125", "100", "50", "30", "130", "130"]

#some common words around which bot chats
menu = ["menu",]
price = ["price", "cost", "rate", "rates", "how much"]
question = ["can", "may", "will", "shall", "would", "should", "give", "server", "deliver"]
ask = ["have", "make", "prepare", "want", "need", "require", "will"]
digits = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


#Check for greeting and reply
def check_for_greeting(sent):
    """If any of the words in the user's input was a greeting, return a greeting response"""
    for word in sent.words:
        if word.lower() in Greetings_Keywords:
            return np.random.choice(Greetings_Responses)

#####
#   Main function controlling the chat flow and to this only api call is made, it returns response        
def respond(sentence):
#    storing query in log file for future use
    logging.error("\n")
    logging.error("question:" + sentence)

#   Cleaning input for i-->I or u --> you and more 
    cleaned = preprocess_text(sentence)

    parsed = TextBlob(cleaned)
    cleaned = cleaned.lower()
    
#   finding pronoun in sentence
    pronoun = find_pronoun(parsed)

#     print(parsed.pos_tags)
    resp = None

    # checking for greeting
    if not resp:
        resp = check_for_greeting(parsed)
    

    # if name of coffee is present then it enters in this loop, then is checked for presence of pronoun, then check if its a question
    # question contains words which suggest an order is being placed 
    if not resp:
        for coffee in coffee_list:
            if re.findall(coffee, cleaned):
                #print(re.findall(coffee, cleaned))
                for w, p in parsed.pos_tags:
                    if p.startswith("PRP"):
                        #print("1")
                        for word in question:
                            if re.findall(word + "\s" + w, cleaned):
                                #print(word)
                                resp = count_coffee(cleaned)
                                #resp = "Sure! a " + coffee + " is on its way. Please wait for sometime."

            # now check is enquiry about coffee is being made with "you" means customer asking something to bot
                for word in ask:
                    for w in parsed.words:
                        #print(w)
                        if w.lower() == 'you':
                            if re.findall("you\s" + word, cleaned):
                                #resp = count_coffee(cleaned)
                                #print("hjk")
                                resp = "Yes we have your choice in our coffee house."
                                
            # now check is enquiry about coffee is being made with "I" means customer saying something to bot
                for word in ask:
                    for w in parsed.words:
                        if w == 'I':
                            if re.findall(r"I\s" + word, cleaned):
                                resp = "Yes sure sir. Right away"

            # Check if user asking for a price
                for word in price:
                    if re.findall(word, cleaned):
                        #x = 50 #fetch price of coffee
                        #resp = "Its our one of best, you can enjoy it at just Rs. 50" 
                        resp = find_price(cleaned)
            #if none matches and sentence has name of coffe, then mostly it will be an order 
                if not resp:
                    resp = count_coffee(cleaned)
                    #resp = "Sure! a " + coffee + "is on its way. Please wait for sometime."



#     has coffee word in query but not specific name so check about if its a question then place order
#     otherwise responce is decided based on sentivity of query 
    if not resp:
        if re.findall(r"coffee", cleaned):
            for word in price:
                if re.findall(word, cleaned):
                    #x = 50 #fetch price of coffee
                    #resp = "Its our one of best, you can enjoy it at just Rs. 50" 
                    resp = find_price(cleaned)
            if not resp:
                parsed.sentiment
                if parsed.sentiment.polarity >= 0.0:
                    resp = "Yes sir\n"+coffee_list_print
                else:
                    resp = "No sir, but why."


#     have menu in query
    if not resp:
        for word in menu:
            if re.findall(word, cleaned):
                resp = coffee_list_print


#     question simple without mention of coffee agin ckeck if its a query otherwise reply accorind sentiment of query
    if not resp:
        for word in question:
            if re.match(word, cleaned):
                for wo in ask:
                    if re.findall(wo, cleaned):
                        resp = coffee_list_print
                if not resp:
                    parsed.sentiment
                    if parsed.sentiment.polarity == 0.0:
                        resp = coffee_list_print
                    elif parsed.sentiment.polarity > 0.0:
                        resp = "We have quite delicious coffes, would you like some\n" + coffee_list_print
                    else:
                        resp = "We have evrtything best"


#        simple sentences with pronoun i or you, reply according to person of sentence
    if not resp:
        if pronoun == "i":
            resp = np.random.choice(Default_response) + np.random.choice(coffee_list) + "."
        elif pronoun == "you":
            resp = np.random.choice(Default_response) + np.random.choice(coffee_list) + "."
    
    #choose random
    if not resp:
        resp = coffee_list_print

    # saving answer in log file with query 
    logging.error("answer:" + resp)
    return resp


# find pronoun
def find_pronoun(sent):
    pronoun = None
    for word, part_of_speech in sent.pos_tags:
        if  part_of_speech.startswith('PRP'):
            pronoun = word.lower()
    return pronoun


# find verb
def find_verb(sent):
    verb = None
    pos = None
    for word, part_of_speech in sent.pos_tags:
        if part_of_speech.startswith('VB'):  # This is a verb
            verb = word
            pos = part_of_speech
            break
    return verb, pos


# find noun
def find_noun(sent):
    noun = None
    if not noun:
        for w, p in sent.pos_tags:
            if p == 'NN':  # This is a noun
                noun = w
                break
    return noun


# preprocessing and cleaning of query
def preprocess_text(sent):
    sent = re.sub(r"(\A|\s)i\s", " I ", sent)
    sent = re.sub("i'm", "I am", sent)
    sent = re.sub("I'm", "I am", sent)
    sent = re.sub(r"(\A|\s)u\s", " you ", sent)
    sent = re.sub(r"u'", "you", sent)
    sent = re.sub(r" +", " ", sent)
    return sent



# count types of coffee with thier respective quantity in query
def count_coffee(sent):
    coffee_name = []
    coffee_count = []

# convery digits(in words into integers, one--->1)
    for digit in digits:
        sent = re.sub(digit, str(digits.index(digit)) , sent)
 
    for coffee in coffee_list:
        if re.findall(coffee, sent):
            sent = re.sub(coffee, remove_space(coffee), sent)

    words = sent.split(" ")
    #print(words)

# find name of coffee preceded by number and in lists... default will be one
    i = 0
    for word in words:
        if re.match(r"[0-9]+$", word):
            for t in coffee_list_r:
                if i+1 < len(words):
                    if re.findall(t, words[i+1]):
                        coffee_name.append(t)
                        coffee_count.append(word)
                        words[i+1] = ""
                        i = i+1
        else:
            i = i+1
    for word in words:
        for t in coffee_list_r:
            if re.findall(t, word):
                coffee_name.append(t)
                coffee_count.append("1")
    #print(coffee_name)
    #print(coffee_count)
    
    # create response based on counts
    if len(coffee_name) == 1:
        if coffee_count[0] == '1':
            resp = "Sure! a " + coffee_list[coffee_list_r.index(coffee_name[0])] + " is on its way. Please wait for sometime."
        else:
            resp = "Sure! " + coffee_count[0] + " " + coffee_list[coffee_list_r.index(coffee_name[0])] + " are on way. Please wait for sometime."
    else:
        resp = "Sir thanks for your order. You have ordered "
        for i in range(0, len(coffee_name)):
            if i == len(coffee_name) - 2:
                resp = resp + coffee_count[i] + " " + coffee_list[coffee_list_r.index(coffee_name[i])] + " and "
            elif i == len(coffee_name) - 1:
                resp = resp + coffee_count[i] + " " + coffee_list[coffee_list_r.index(coffee_name[i])] + ".Please wait for sometime."
            else:
                resp = resp + coffee_count[i] + " " + coffee_list[coffee_list_r.index(coffee_name[i])] + ", "  

    ######## Bill generation can be done here only and returned             # 
    return resp


# remove spaces from words
def remove_space(word):
    return re.sub("\s", "", word)


# returns a response containing price of all the coffe names mentioned in query
def find_price(sent):
    x = 50 #fetch price of coffee
    #resp = "Its our one of best, you can enjoy it at just Rs. 50"
    temp = 0
    coffee_name = []

    # count coffee names
    for coffee in coffee_list:
        if re.findall(coffee, sent):
            temp = temp+1
            coffee_name.append(coffee)
    
    # generate responses
    if temp == 1:
        x = 50 #fetch price of coffee_name[0]
        resp = "Its our one of best, you can enjoy it at just Rs. " + price_coffee[coffee_list.index(coffee_name[0])]
    elif temp == 0:
        resp = coffee_list_print
    else:
        resp = "Sir "
        for i in range(0, len(coffee_name)):
            x = 50 # fetch price for coffee_name[i]
            if i == len(coffee_name)-1:
                resp = resp + coffee_name[i] + " is of Rs. " + price_coffee[coffee_list.index(coffee_name[0])]
            else:
                resp = resp + coffee_name[i] + " is of Rs. " + price_coffee[coffee_list.index(coffee_name[0])] + ", " 
    return resp