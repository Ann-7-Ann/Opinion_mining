import re
import nltk
from nltk.corpus import opinion_lexicon
nltk.download('opinion_lexicon')

cleaned_reviews = []
with open("reviews.txt", "r", encoding="utf-8") as file:
    temp = []
    for line in file:
        line = line.strip()  # remove leading/trailing whitespace
        temp.append(line)
        if re.match(r"^\d\s*/\s*\d$", line):   # when rating present == review end
            cleaned_reviews.append(" ".join(temp))  # upload review
            temp = []
        

all_phrases= []
for review in cleaned_reviews:
    tokens = nltk.word_tokenize(review)
    pos_tags = nltk.tag.pos_tag(tokens, tagset=None, lang='eng')
    # Filter out 'DT' (determiners)
    pos_tags = [ (word, tag) for word, tag in pos_tags if tag != 'DT' ]
    phrases = []
    for i in range(len(pos_tags)):
        word1, tag1 = pos_tags[i]

        # Ensure enough tokens are available
        word2, tag2 = pos_tags[i + 1] if i + 1 < len(pos_tags) else (None, None)
        word3, tag3 = pos_tags[i + 2] if i + 2 < len(pos_tags) else (None, None)
        word4, tag4 = pos_tags[i + 3] if i + 3 < len(pos_tags) else (None, None)

        # 1. Adjective + Noun
        if tag1.startswith("JJ") and tag2 and tag2.startswith("NN"):
            phrase = f"{word1} {word2}"
            #print("adjective noun:", phrase)
            phrases.append(phrase)

        # 2. Verb + Noun (object phrases)
        # if tag1.startswith("VB") and tag2 and tag2.startswith("NN"):
        #     phrase = f"{word1} {word2}"
        #     print("verb noun:", phrase)
        #     phrases.append(phrase)

        # 3. Adverb + Adjective + Noun
        if tag1.startswith("RB") and tag2 and tag2.startswith("JJ") and tag3 and tag3.startswith("NN"):
            phrase = f"{word1} {word2} {word3}"
            #print("adverb adjective noun:", phrase)
            phrases.append(phrase)

        # 4. Noun + Verb + Adjective
        if tag1.startswith("NN") and tag2 and tag2.startswith("VB"):
            # 3rd is adjective
            if tag3 and tag3.startswith("JJ"):
                phrase = f"{word1} {word2} {word3}"
                #print("noun verb adjective:", phrase)
                phrases.append(phrase)
            # adverb(negation) and 4th is adjective
            if tag3 and tag3.startswith("RB") and tag4 and tag4.startswith("JJ"):
                phrase = f"{word1} {word2} {word3} {word4}"
                print("noun verb # adjective:", phrase)
                phrases.append(phrase)

    positive = set(opinion_lexicon.positive())
    negative = set(opinion_lexicon.negative())

    def check_polarity(phrase, positive, negative):
        words = phrase.lower().split()
        pos_count = sum(1 for word in words if word in positive)
        neg_count = sum(1 for word in words if word in negative)

        if words.count('not') > 0:
            pos_count, neg_count = neg_count, pos_count
        if pos_count > neg_count:
            return "+"
        elif neg_count > pos_count:
            return "-"
        elif pos_count == 0 and neg_count == 0:
            return "neutral"
        else:
            return "mixed"

    assesed = []  
    for phrase in phrases:
        value = check_polarity(phrase, positive, negative)
        assesed.append((phrase, value))
    all_phrases.append(assesed)

    #print(assesed)
    with open("phrases.txt", "w", encoding="utf-8") as f:
        for i, review_phrases in enumerate(all_phrases, start=1):
            f.write(f"Review {i}:\n")
            f.write(str(review_phrases))  # writes list of tuples as string
            f.write("\n\n")  # blank line between reviews
