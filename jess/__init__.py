from .ruleparser import RuleParser, find
from copy import deepcopy

class Issue(Exception):
    def __init__(self, problem):
        self.problem = problem
    def __str__(self):
        return 'ERROR: the problem was: %s' % self.problem

"""
Action is used to take soup and a rule file and extract the soup based on the
rule file into a dictionary. The rule file is composed of identifiers (CSS) and
lines of code like in a css file. The lines of code take three forms
key: get(css_identifier<search identifier>);
key: name;
val: name;

having one of the two keys is mandatory, but value is not. You cannot have more
than one value, and not more than one key. The get type key code searches for
the closest tag (based on the selected search) and assigns that tags key to the
current tags (given by the rule's identifier). Note that such a key must have already
been created. The searches are up (parent to parent of parent, etc. and their left-wise
siblings), left (siblings), and right (siblings). The corrsponding search identifiers
are ^, <, and >. If a name is given for either key or value. Each tag that is found
with the rule's identifier will be passed to a function given that name in the Action
object. The function will return a value that will be used as either the key or
value, depending on the keyword you use in the rule code (key or val)

Note that multiple values can be assigned to the same key. The dictionary that
Action creates has values that are lists. The keys are the ones you created (given
your rule set), and the values that you created comprise the aforementioned lists.

Also note that the rules are executed in the order the are written.

To input a set of functions and their corresponding names. Input a dictionary
with names as keys and function instances as values to Action using its
SetWeapons method.

--------------------------------------------------------------------------------
To use action:

create a <name_of_file>.css file containing your rules
then in your code generate the soup that you wish to extract.
create your functions, and the corresponding function dictionary
(or weapons dictionary :D)
Then write something like the following:
action = Action()
action.LoadPlan(<path to css like file>)
action.SetWeapons(weapons_dictionary)
action.SetVillain(your_soup)
action.Act()
result_dictionary = action.DumpVillain()
"""

class Action:

    def __init__(self, plan_address, function_dictionary):
        self.key_lists = {}   # the keys for this list are identifiers, the
                                # values are lists of tag key pairs (if there
                                # is no key, None is kept there)
        self.tag_lists = {}
        self.soup = None
        self.functions = None
        self.rules = None
        self.fields = {}
        self.LoadPlan(plan_address)
        self.SetWeapons(function_dictionary)

    def LoadPlan(self, file_address):
        # this creates a RuleParser and adds the css like file to it
        # and then parses that css like file
        self.rules = RuleParser()
        self.rules.GetContent(file_address)
        self.rules.ParseContent()

    def SetWeapons(self, function_dictionary):
        # this sets the name -> function dictionary
        # each of the names in your css like file should be in this dictionary
        # with a corresponding function that takes only a tag as input
        self.functions = deepcopy(function_dictionary)

    def SetVillain(self, fly_soup):
        # this sets the soup you will be extracting data from
        # it will also reset everything in preparation for this new villain
        self.soup = fly_soup
        self.fields = {}
        self.tag_lists = {}
        self.key_lists = {}

    def Act(self):
        # this will run through the rules gathered from the css like file
        # and execute each one in order the result will be the filling up
        # of your fields
        for identifier in self.rules:
            self.executeRule(identifier)

    def DumpVillain(self):
        # this returns a copy of the fields for your consumption
        return deepcopy(self.fields)

    def executeRule(self, identifier):
        # this uses the identifier to grab and parse the rule using
        # the parseRule function. This returns a value function
        # or "" if no value is to be generated from the rule, a key function
        # or request for getting an already generated key, and a boolean
        # that lets us know if already generated keys are requested
        # it then calls the appropriate tag handler
        value_function, key_create, get_key = self.parseRule(identifier)
        if get_key:
            self.handleTags_GetKeys(identifier, value_function, key_create)
        elif value_function:
            self.handleTags_CreateKeys(identifier, value_function, key_create)
        else:
            self.handleTags_OnlyKeys(identifier, key_create)

    def parseRule(self, identifier):
        # This grabs the rule from self.rules by key, then returns a value function
        # or "" if no value is to be generated from the rule, a key function
        # or request for getting an already generated key, and a boolean
        # that lets us know if already generated keys are requested
        # it then calls the appropriate tag handler
        key_create = ""
        value_function = ""
        # we work our way through the lines of code
        for line in self.rules[identifier]:
            # we look to see if we have key or val
            if line[:3] == "key":
                key_create = line[4:].strip()   # we get rid of 'key:'' and the resulting space
            elif line[:3] == "val":
                value_function = self.functions[line[4:].strip()]  # we get rid of 'key:'' and the resulting space
                    # and we grab the function corresponding to the name found
        # next we check if the key_create is a get(identifier)
        if len(key_create) > 4 and key_create[:3] == "get":
            # if so we set get_key to True and grab the identifier in the parens
            get_key = True
            key_create = key_create[4:-1]
        else:
            # otherwise we get the function to generate the keys and we set
            # get_key to False
            get_key = False
            key_create = self.functions[key_create]
        return value_function, key_create, get_key

    """
    Now we allow for the following functionality: a rule may specify simply creating
    a key. Then another rule may ask to get those keys. And a search will be done
    to find the key corrsponding to the closest tag, given the type of search.
    As such we need to key an two corresponding ordered lists of keys and tags, one pair
    of such lists per identifier (all identifiers must have at least keys). As such
    whenever we add a key, or use a key for an identifier, we will add to the key
    list and tag list under that identifier in the corresponding key_lists and tag_lists
    that are attributes of this object.
    """
    def handleTags_GetKeys(self, identifier, value_function, key_identifier):
        # first we get the identifier for which kind of search we are going to use
        search_key = key_identifier[-1]
        # next we get the identifier for the rule we will be getting the key from
        key_identifier = key_identifier[:-1]
        # we set the search function. The search function will take the key_identifier
        # and the tag you are performing the search for and will return the index
        # of the key for the key_list under the key_identifier key in self.key_lists
        if search_key == "^":
            search = self.searchUp
        elif search_key == ">":
            search = self.searchRight
        elif search_key == "<":
            search = self.searchLeft
        # next we get the tags satisfying the css identifier
        tags = self.soup.select(identifier)
        # we prepare for adding the keys so that they can be accessed by other rules
        if identifier not in self.key_lists:
            self.key_lists[identifier] = []
        if identifier not in self.tag_lists:
            self.tag_lists[identifier] = []
        # we run through the tags
        for tag in tags:
            # we create the value
            value = value_function(tag)
            # we get the index of the key using our selected search
            key_index = search(tag, key_identifier)
            # we check to make sure the key exists
            if key_index == -1:
                raise Issue("no key found for identifier %s" % identifier)
            # we get the key
            key = self.key_lists[key_identifier][key_index]
            # we add the key value pair to fields
            self.addValue(key, value)
            # now we add the key and tag to the lists
            self.key_lists[identifier].append(key)
            self.tag_lists[identifier].append(tag)


    def handleTags_CreateKeys(self, identifier, value_function, key_function):
        # this will be easier because we create the keys
        tags = self.soup.select(identifier)
        # we prepare for adding the keys so that they can be accessed by other rules
        if identifier not in self.key_lists:
            self.key_lists[identifier] = []
        if identifier not in self.tag_lists:
            self.tag_lists[identifier] = []
        for tag in tags:
            # we create the value
            value = value_function(tag)
            # we create the key
            key = key_function(tag)
            # we add the key value pair to fields
            self.addValue(key, value)
            # now we add the key and tag to the lists
            self.key_lists[identifier].append(key)
            self.tag_lists[identifier].append(tag)

    def handleTags_OnlyKeys(self, identifier, key_function):
        # here we are just creating keys and adding them to those two lists
        tags = self.soup.select(identifier)
        # we prepare for adding the keys so that they can be accessed by other rules
        if identifier not in self.key_lists:
            self.key_lists[identifier] = []
        if identifier not in self.tag_lists:
            self.tag_lists[identifier] = []
        for tag in tags:
            # we create the key
            key = key_function(tag)
            # now we add the key and tag to the lists
            self.key_lists[identifier].append(key)
            self.tag_lists[identifier].append(tag)

    def addValue(self, key, value):
        # in adding values, we would like to be able to assign many values
        # to the same key
        if key in self.fields:
            self.fields[key].append(value)
        else:
            self.fields[key] = [value]


    def searchUp(self, tag, identifier):
        # this will search up through parent after parent checking left-wise
        # siblings as well. As soon as it finds a match in the tag list for the
        # input identifier it will return the index of that tag
        tag_list = self.tag_lists[identifier]
        # so we will search up and out, up and out
        parent = tag.parent
        while parent:
            # now we search through the parent and its leftwise siblings
            if parent in tag_list:
                index = find(parent, tag_list)
                return index
            sibling = parent.previous_sibling
            while sibling or isinstance(sibling, str):
                if sibling in tag_list:
                    index = find(sibling, tag_list)
                    return index
                sibling = sibling.previous_sibling
            parent = parent.parent
        # if we didn't find anything return -1
        return -1

    def searchRight(self, tag, identifier):
        # this searches rightwise siblings. s soon as it finds a match in the tag list for the
        # input identifier it will return the index of that tag
        tag_list = self.tag_lists[identifier]
        sibling = tag.next_sibling
        while sibling or isinstance(sibling, str):
            if sibling in tag_list:
                index = find(sibling, tag_list)
                return index
            sibling = sibling.next_sibling
        return -1

    def searchLeft(self, tag, identifier):
        # this searches leftwise siblings. s soon as it finds a match in the tag list for the
        # input identifier it will return the index of that tag
        tag_list = self.tag_lists[identifier]
        sibling = tag.previous_sibling
        while sibling or isinstance(sibling, str):
            if sibling in tag_list:
                index = find(sibling, tag_list)
                return index
            sibling = sibling.previous_sibling
        return -1
