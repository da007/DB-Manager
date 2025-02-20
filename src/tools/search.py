import Levenshtein

def is_perhabs_match(string1,string2):
    return Levenshtein.ratio(string1, string2) >= 0.7 or string1 in string2