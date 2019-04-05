from imdb import IMDb
import json



def get_keywords(genre):

    ia = IMDb()
    unfiltered_words = ia.search_keyword(genre)

    stopwordsfile = open("./staticfiles/stopwords.txt", 'r+' )
    stopwords = stopwordsfile.read().splitlines()
    stopwordsfile.close()
    filtered_words = []
    #loop through unfiltered keywords
    for word in unfiltered_words:
        safe = True

        if genre not in word:
            safe = False

        #check all stopwords
        else:
            for sw in stopwords:
                #if keyword includes stopword it is not safe
                if sw in word:
                    safe = False
                    #stop loop if word is not safe
                    break

        if safe:
            filtered_words.append(word)

    return filtered_words


def get_movies(key_words):
    ia = IMDb()
    movies = []
    for word in key_words:
        list = ia.get_keyword(word)
        for movie in list:
            if movie["kind"] is "movie":
                movies.append(movie)

    return movies

def get_first_common(user, other_user, type):
    if len(other_user) < len(user):
        size = len(user)
    else:
        size = len(other_user)
    i=0

    temp = []
    while i < size:
        try:
            if user[i][type]  in temp:
                return user[i][type]
            else:
                temp.append(user[i][type])
        except:
            pass
        try:
            if other_user[i][type] in temp:
                return other_user[i][type]
            else:
                temp.append(other_user[i][type])
        except:
            pass

        i += 1

    return False

def get_commons(user, other_user, type):
        if len(other_user) < len(user):
            size = len(user)
        else:
            size = len(other_user)
        i=0

        temp = []
        commons = []
        while i < size:
            try:
                if user[i][type]  in temp:
                    commons.append(user[i][type])
                else:
                    temp.append(user[i][type])
            except:
                pass
            try:
                if other_user[i][type] in temp:
                    commons.append(other_user[i][type])
                else:
                    temp.append(other_user[i][type])
            except:
                pass

            i += 1

        return commons
