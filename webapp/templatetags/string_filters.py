# Copyright (C) 2011 Philter Phactory Ltd.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X
# CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# Except as contained in this notice, the name of Philter Phactory Ltd. shall
# not be used in advertising or otherwise to promote the sale, use or other
# dealings in this Software without prior written authorization from Philter
# Phactory Ltd..
#

import re
from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter
@stringfilter
def with_indefinite_article(phrase, before_phrase="", after_phrase=""):
    silent_h_words = ["homage", "hour", "herb", "heir", "honest", "honor"]
    letters_with_initial_vowel_sound = ["a", "e", "f", "h", "i", "l", "m", "n", "o", "r", "s", "x"]
    vowels = ["a", "e", "i", "o", "u"]
    o_exceptions = ["once","one","oneness","ones","oneself","onetime"]
    u_exceptions = ["ubiquitous","uganda","ugandan","ukraine","ukrainian","ukulele","ukuleles","unanimous","unanimously","unicellular","unicorn","unicorns","unicycle","unicycles","unification","unified","uniform","uniformed","uniformly","uniforms","unify","unifying","unilateral","unilateralism","unilaterally","union","unionist","unionists","unionization","unionized","unionizing","unions","unique","uniquely","uniqueness","unisex","unison","unisons","unit","unitarian","unitary","unite","united","uniting","units","unity","universal","universally","universe","universes","universities","university","universitys","unix","uranium","urinalysis","urinary","urinate","urinating","urine","urologist","urologists","urology","uruguay","uruguayan","uruguays","usable","usage","usages","use","used","useful","usefully","usefulness","useless","usenet","user","users","uses","usual","usually","usurp","usurpation","usurped","usurper","usurping","usury","utah","utahn","utahns","utahs","utensil","utensils","uterine","utero","uterus","utilitarian","utilities","utility","utilitys","utilization","utilize","utilized","utilizes","utilizing","utopia","utopian","utopians","utopias"]
    split_phrase = phrase.split()
    if not len(split_phrase):
        return "%s %s%s" % (before_phrase, phrase, after_phrase)
    # get rid of everything but letters and numbers and a few characters
    first_word = re.sub(r"[^A-Za-z0-9\-]", "", split_phrase[0])
    first_letter = first_word[0].lower()
    # default to 'a'
    article = "a"
    if first_word.isupper() or (len(first_word) == 1):
        # if all caps or a single letter, we're going to assume it's an abbreviation
        if first_letter in letters_with_initial_vowel_sound:
            article = "an"
    elif first_letter == "h" and any( [re.match(r'(?i)%s' % w, first_word) for w in silent_h_words] ):
        article = "an"
    elif first_letter in vowels:
        if first_letter == 'e':
            article = "a" if first_word.lower().split('-')[0] == 'ewe' else "an"
        elif first_letter == 'o':
            article = "a" if first_word.lower().split('-')[0] in o_exceptions else "an"
        elif first_letter == 'u':
            article = "a" if first_word.lower().split('-')[0] in u_exceptions else "an"
        else:
            article = "an"
    return "%s %s%s%s" % (article, before_phrase, phrase, after_phrase)


@register.filter
@stringfilter
def str_replace(string_phrase, chars="_.", with_char=" "):
    "Removes all values of replace_chars from the given string and replaces with with_char"
    for char in list(chars):
        string_phrase = string_phrase.replace(char, with_char)
    return string_phrase
