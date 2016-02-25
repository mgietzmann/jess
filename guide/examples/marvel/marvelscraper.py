from jess import Action

# Here are our extraction functions

def bold(tag):
    # this gets the content from the bold tag
    return tag.b.get_text().strip()

def unmarkedtext(tag):
    # this gets the text from all of the children
    # of the paragraph (strings are counted as children) from
    # after the second tag onwards (the second child is a bold tag for
    # the paragraphs we will be extracting data from with
    # this function)
    string = ''
    count = 0
    for child in tag.children:
        if count > 1:
            try:
                string = string + child.get_text()
            except:
                string = string + child
        count += 1
    return string

def text(tag):
    # just grabs all of the text
    return tag.get_text().strip()

def blocks(tag):
    # this will get the number of blocks diplayed in this tag
    styling = tag.attrs['style']
    # styling in the page is of the form width:[numbers]px;
    # we want to just get the number of pixels so we know
    # how wide it is.
    width = styling[6:-3]
    # now depending on the width, we return the number of blocks
    if width == '21':
        return 1
    elif width == '42':
        return 2
    elif width == '63':
        return 3
    elif width == '84':
        return 4
    elif width == '105':
        return 5
    elif width == '126':
        return 6
    else:
        return 7

def firstchild(tag):
    for child in tag.children:
        # have to do this to actually make it a string
        return str(child)


def content(tag):
    # this simply returns the constant string 'Content'
    return 'Content'

# here is our function dictionary
weapons = {'firstchild' : firstchild, 'bold': bold, 'unmarkedtext': unmarkedtext, 'text': text, 'blocks': blocks, 'content': content}

# here is our action
action = Action('marvelscraper.css', weapons)

# now we get our soup
from urllib2 import urlopen
from bs4 import BeautifulSoup
html = urlopen('http://marvel.com/universe/Scarlet_Witch_%28Wanda_Maximoff%29').read()
soup = BeautifulSoup(html, 'lxml')

# we input our soup into the action
action.SetVillain(soup)
# we scrape the page
action.Act()
# and now we grap the resulting dictionary
beaten = action.DumpVillain()

# this function does some post processing on the scraping result
def postProcessVillain(dumped_villain):
    # now there are a couple of things we want to do to the resulting dictionary
    # first we want to concatenate the content strings into one content string
    content_string = ''
    for string in dumped_villain['Content']:
        content_string = content_string + string
    dumped_villain['Content'] = content_string

    # then for the values we got from the sidebar, we want to split by
    # comma
    for key in dumped_villain:
        # we make sure we are grabbing something from the sidebar
        if not key == 'Content' and not isinstance(dumped_villain[key][0], int):
            string = dumped_villain[key][0] # remember all values are a list, even if it
                                # is a list of one element
            strings = string.split(',')
            new_strings = []
            # we just want to strip whitespace now
            for string in strings:
                string = string.strip()
                new_strings.append(string)
            # now we assign these new values to the key
            dumped_villain[key] = new_strings
    return dumped_villain

# now we print the results! :D
print(postProcessVillain(beaten))
