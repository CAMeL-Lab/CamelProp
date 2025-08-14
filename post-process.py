''''
This script is the code implementation of post-processing edits described in: https://arxiv.org/abs/2505.02656
All the functions below process text in Buckawalter tranliteration, ans retruns results in
Buckwalter transliteration as well. 
'''

import re
from camel_tools.utils.charmap import CharMapper
from camel_tools.utils.charsets import AR_CHARSET, AR_DIAC_CHARSET


ar2bw = CharMapper.builtin_mapper("ar2bw")

#################### Letter clean up ####################
## This function normalizes Persian to Arabic letters and normalizes persian yaa to y

def fix_farsi(word):
    word_clean = ""
    ar_clean = CharMapper.builtin_mapper('arclean')
    ar2bw = CharMapper.builtin_mapper('ar2bw')
    bw2ar = CharMapper.builtin_mapper('bw2ar')
    try:
        word_og = set(word)
    except:
        import pdb;pdb.set_trace()    
    word = bw2ar(word)
    for char in word: 
        if char not in AR_DIAC_CHARSET:
            #if char != ar_clean(char):
                #print(char,ar_clean(char))
            char = ar_clean(char)
        word_clean+=char
    #word_clean=ar_clean(word)
    if word != word_clean: 
        word_clean = word_clean.replace("ى","ي")
        
    if word_og.intersection(AR_CHARSET):
        return word_clean
    else: 
        #word_clean = bw2ar(word_clean)
        return ar2bw(word_clean)


#################### Diacritization improvements ####################
#  
### This function removes Fatha that follows an Alif Madda (آ)
def remove_a_after_madda(text):
  text = ar2bw(text)
  return text.replace('|a','|')

### This function adds a Fatha bafore Alif Madd where it is missing
def add_fatha_before_alif(text):
    text = ar2bw(text)
    pattern = r'(?<!^)(?<!a)A'
    # Replace all matched "A"s with "aA"
    result = re.sub(pattern, r'aA', text)
    return result
    
### This function adds a Kasra after Hamza below where it is missing
def add_i_after_hamza(word):
    word = ar2bw(word)
    return re.sub(r'^<(?!i)(.)', lambda m: '<i' if m.group(1) in 'uoa' else f'<i{m.group(1)}', word)
    
### This ensures that a diacritic always comes after the shadda
def fix_shadda(lemma):
  lemma = ar2bw(lemma)
  return re.sub(r'([aiuo])~', r'~\1', lemma)

### This function removes diacritics on long vowels where they're mistakenly added
def remove_diacritic_after_madd(word):
    word = ar2bw(word)
    pattern = r'(iy|uw|aA)(~?[a|u|o|i|~])'

    # Replace the matching 'o' with an empty string
    result = re.sub(pattern, r'\1', word)

    return result

### This removes case endings , final possition diacritics
def remove_case_ending(word):
   word = ar2bw(word)
   pattern = r"([.*\S])([a|u|o|i|K|N|F])$"
   result = re.sub(pattern, r'\1', word)
   return result

#### A wrapper function that applies all the above steps
def apply_fixes_safe(word):
   word = ar2bw(word) 
   return remove_case_ending(add_fatha_before_alif(remove_a_after_madda(add_i_after_hamza(fix_shadda(remove_a_after_madda(word))))))

### This adds Sukuns on consonant (not long vowels or glides) letters where they're missing, after all the other fixes have been applied 
def add_sukoon(word):
    word = ar2bw(word) 

    constants_all = ['b','t','v','j','H','x','d',r'\*','r','z','s',r'\$','S','D','T','Z','E','g','f','q','k','l','m','n','h','Y','p',r'\{',r'\}']
    pattern = r'([{0}])(?=[{0}])'.format(''.join(re.escape(char) for char in constants_all))
    #match = re.findall(pattern, word)
    modified_string = re.compile(pattern).subn(r"\1o",word)
    return modified_string[0]

#################### Well-formedness checks ####################

### This checks if a word is a valid diacritized lemma based on the criteria described in: https://arxiv.org/abs/2505.02656

def is_valid_diac(lemma):
    lemma = ar2bw(lemma) 
    consonants_all = ['b','t','v','j','H','x','d',r'\*','r','z','s',r'\$','S','D','T','Z','E','g','f','q','k','l','m','n','h',r'\<',r'\>',r"\&",r"\}",r"\{","'"]
    lond_vowel =['iy','aA','uw']
    diacritics =['a`','i','u']
    c_regex = r"("+'|'.join(consonants_all)+r")"
    madd_regex = r"(~?("+'|'.join(lond_vowel)+r"))"
    diac_mark = r"(~?["+'|'.join(diacritics)+r"|a`]|o)" #added Dagger alif because it follows the same rules 
    #print(diac_mark)
    start_match = r'(\|?'+r"("+c_regex+r"|y|w)"+r")"
    mid_match =r'('+diac_mark+r"|"+madd_regex+r")|\|"
    end_match = r'('+c_regex+r"|y|A|w|Y|p)~?"
    valid_lemma_regex = r"^(("+start_match+mid_match+r")*"+end_match+r")$"
    valid_lemma_regex=re.compile(valid_lemma_regex)
    if not valid_lemma_regex.match(lemma.strip()):
        
        return 1
        #return re.match(valid_lemma_regex,lemma)
    else:
        #return re.match(valid_lemma_regex,lemma)
        return 0


print(is_valid_diac("hay"))
