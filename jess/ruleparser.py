# Python File ruleparser.py

def find(element, list):
    try:
        return list.index(element)
    except:
        return -1

"""
This file contains the code for grabbing rules from CSS files. The code is
really simple but will make things much more convenient.

A CSS rule is made of two things:
    * an identifier which lets us know which tags we are dealing with
    * lines of code

The lines of code are made distinct by the curly braces that wrap them.
And the identifiers are composed of what I will call types and relations.
Types tell us what the individual tags that compose the identifier are. They
can be just tag names, or a . or # followed by a class or id respectively.
The relations are ' ', ~, >, + all identifying some kind of relation between
the tags composing the identifier. Finally, one block of code can have several
identifiers corresponding to it. This is shown with the identifiers between comma
separated.

The following code contains functions for removing comments from CSS content,
taking the block of lines and separating them out (they are separated by
semicolons), and then putting that together, grabbing identifiers and code lines
and putting them into a final object that represents the rules.

The object that the rules are placed in acts like a dictionary with the additional
feature that iterating through the keys will iterate in the order you added them.
Therefore we have an ordered dictionary. This object is wrapped in a further object
which has two convenience methods so you only need deal with it. The first method
allows you to add content straight from a file. The second is a call to the function
that parses out the content into the object on hand.

Therefore, to parse the rules of a css file with address file_ad you do the following:
rules = RuleParser()
rules.getContent(file_ad)
rules.parseContent()

and then you can access the rules in order by iterating through keys
and you can retrieve the lines of code per identifier with
rules[identifier]
"""

import re

# here are the regular expressions which will ease our parsing
comment_re = re.compile('\/\*[^(?:\/\*)]*\*\/')
rule_ex = re.compile('(\S[^\{\}]*)\s\s*\{\s*([^\{\}]*[\S])\s*\}')
# this expression captures both the identifier (list) and the code without any trailing or
# preceeding whitespace
line_ex = re.compile('[^;\n]{1,};') # this provides a match to a single code line

def removeComments(file_content):
    # this will go through and make matches to comment_re and remove these
    matches = re.findall(comment_re, file_content)
    # now we go backwards through the list of matches
    # and make our edits
    for i in range(-1, -len(matches) - 1, -1):
        match = matches[i]
        start = matche.start()
        end = matche.end() # note this is the start of the string after the
                            # match, given how match.end() works
        file_content = file_content[:start] + file_content[end:]
    return file_content

def getLines(code):
    # code is a string and we are going to use the line_ex to grab every line found
    # append each line (without the semicolon and trailing whitespace that may
    # result) to a list, and return that list
    lines = []
    for match in re.finditer(line_ex, code):
        # we need to remove the semicolon and any remaining whitespace that might
        # result from that removal
        line = match.group(0)
        line = line[:-1].strip()    # the semicolon should be at the end of the line
        lines.append(line)
    return lines

# this takes a rules object, so a rules object can call this on itself
def getRules(css_like_content, rules_object):
    # first we remove contents
    content = removeComments(css_like_content)
    # now we find all the matches for rule_ex in the content
    for rule in re.finditer(rule_ex, content):
        # for each we grab the indentifier string and split by comma
        identifiers = rule.group(1).split(",")
        # then we get the lines of code
        lines = getLines(rule.group(2))
        # and for each identifier, we strip additional whitespace and add the
        # lines under that indentifier thus create a new rule in our rules_object
        for identifier in identifiers:
            identifier = identifier.strip()
            rules_object[identifier] = lines

# here is the ordered dictionary class
class OrderedDictionary:

    def __init__(self):
        self.key_list = []
        self.dictionary = {}
        self.current_index = 0

    def __setitem__(self, key, value):
        self.dictionary[key] = value
        index = find(key, self.key_list)
        if not index == -1:
            self.key_list.pop(index)
        self.key_list.append(key)

    def __getitem__(self, key):
        return self.dictionary[key]

    def __iter__(self):
        return self.key_list.__iter__()

    def next(self):
        to_return = self.dictionary[self.key_list[self.current_index]]
        self.current_index += 1
        return to_return

# and here is the convenience wrapper object
class RuleParser(OrderedDictionary):

    def GetContent(self, file_address):
        file = open(file_address, 'r')
        self.content = file.read()

    def ParseContent(self):
        getRules(self.content, self)
