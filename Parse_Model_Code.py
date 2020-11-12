class ComplexStruct:
    def __init__(self, complexName, Child):
        self.N = complexName
        self.Child = Child


class Attribute:
    def __init__(self, name):
        self.Name = name
        self.Attribute = '__attribute__'


'''---------------- Function to Deal with the clinical trial XML Pattern------------------'''

# Make a list of all complexType which define a structure of a variable
def get_complex_type(root):
    complex_type_name = []
    list_complex_struct = []
    for child in root.iter('{http://www.w3.org/2001/XMLSchema}complexType'):
        if isinstance(child.get('name'), str) and child.get('name') is not None:
            # Storing a class containing two attribute, name and the structure (child)
            list_complex_struct.append(ComplexStruct(child.get('name'), child))
            complex_type_name.append(child.get('name'))
    return complex_type_name, list_complex_struct


def get_structure(child, complex_type_name, list_complex_struct, memory_name):
    list_name = []
    list_one = []
    for children in child.iter('{http://www.w3.org/2001/XMLSchema}element'):
        name = children.get('name')
        type = children.get('type')
        if type is not None:
            list_name.append(name)
            if type in complex_type_name: # identify complex structures
                index = complex_type_name.index(type)
                # Loop into the complex structure
                for grandchild in list_complex_struct[index].Child:
                    # Loop to retrieve the name
                    memory_name = name
                    list_one.extend(get_structure(grandchild, complex_type_name, list_complex_struct, memory_name))
                # Store the structure in list
                if len(list_one) > 0:
                    list_name.append(list_one)
                list_one = []
    # in the complex structure, there often is extension and attribute which needs to be displayed
    # they is never a complex structure in the extension or in the attribute so the name is simply added to the list.
    for children in child.iter('{http://www.w3.org/2001/XMLSchema}extension'):
        if isinstance(children.get('base'), str):
            list_name.append(memory_name)
    for children in child.iter('{http://www.w3.org/2001/XMLSchema}attribute'):
        if children.get('name') != 'rank':
            name = Attribute(children.get('name'))
            list_name.append(name)
    return list_name

def get_major_titles(Pattern):
    """Get the headers"""
    import xml.etree.ElementTree as ET
    tree = ET.parse(Pattern)  # File in the project taken as a reference of the files architecture
    root = tree.getroot()
    major_title = []
    for child in root.findall('{http://www.w3.org/2001/XMLSchema}element'):
        for children in child.iter('{http://www.w3.org/2001/XMLSchema}element'):
            if child != children:
                name = children.get('name')
                major_title.append(name)
    return major_title


# Return a List of the structure as follow : [Ep1,[Es1,Es2[Es11,Es12],Es3],Ep2...]
# Pattern is the xml file stored in the folder
# User List is retrieved from the User Interface
def parse_model(Pattern, UserList):
    """This Function Parse the XML Schema"""
    import xml.etree.ElementTree as ET
    structural_user_List=[]
    tree = ET.parse(Pattern)
    root = tree.getroot()
    # Get all the Major Title from the Pattern
    major_list = get_major_titles(Pattern)
    for element in UserList:
        if element in major_list:
            major_list.remove(element)
    # get the variables to inject in below functions
    complex_type_name, ListComplexStruct = get_complex_type(root)
    # go to clinical study directly (0 iteration)
    for grand_child in root.findall('{http://www.w3.org/2001/XMLSchema}element'):
        # go to sequence (0 iteration)
        for child in grand_child.iter('{http://www.w3.org/2001/XMLSchema}sequence'):
            # child is the list of all headers
            for children in list(child.iter('{http://www.w3.org/2001/XMLSchema}element')):
                # children is a header in the list
                if children.get('name') in major_list:
                    # Reducing the root to only what we need (UserListStructure)
                    child.remove(children)
        # Get structure by calling the below function
        structural_user_List = get_structure(child, complex_type_name, ListComplexStruct, '')
    return structural_user_List


def number_of_rows(List):
    list_counter = []
    for child in List:
        counter = 0
        if isinstance(child, list):
            y = number_of_rows(child)
            counter = 1 + y
        list_counter.append(counter)
    return max(list_counter)


def counter_column(list_one, counter):
    """Count number of column for each main header
    important function to count the number of space between two main header"""
    for child in list_one:
        if isinstance(child, list):
            counter -= 1
            counter = counter_column(child, counter)
        else:
            counter += 1
    return counter


def take_name(List):
    """Replace Attribute class element by the element name"""
    list_of_names = []
    for i in range(len(List)):
        if isinstance(List[i], Attribute):
            x = List[i]
            list_of_names.append(x.Name)
        elif isinstance(List[i], list):
            list_of_names.append(take_name(List[i]))
        else:
            list_of_names.append(List[i])
    return list_of_names


def header(List):
    """Create a List of Element displayed in the CSV for one line"""
    headers = []
    restes = []
    for element in List:
        if isinstance(element, str):
            restes.append('')
            headers.append(element)
        elif isinstance(element, list):
            counter = 0
            restes.pop()
            restes.extend(element)
            for i in range(counter_column(element, counter) - 1):
                headers.append('')
    return headers, restes


def headers(List, nombre_de_ligne):
    list_one = []
    restes = List
    for i in range(nombre_de_ligne):
        list_header, restes = header(restes)
        list_one.append(list_header)
    return (list_one)


# The following function takes the List of Headers and create one complete list of the last header display
# ['Ep1','','','Ep2','Ep3','']+['Es1','Es2','Es3','','Es1','Es2'] goes->['Es1','Es2','Es3','Ep2','Es1','Es2']
def realign_all_headers(Headers):
    """Create list of the last plotted header in every column"""
    complete_list = []
    for i in range(len(Headers[len(Headers) - 1])):
        if (Headers[len(Headers) - 1][i]) != '':
            complete_list.append(Headers[len(Headers) - 1][i])
        else:
            for j in range(1, len(Headers)):
                if (Headers[len(Headers) - j - 1][i]) != '':
                    complete_list.append(Headers[len(Headers) - j - 1][i])
                    break
    return complete_list

def retrieve_nct_number(root):
    nct_number=''
    for child in root.iter('nct_id'):
        nct_number=child.text
    return nct_number

def main_search_v01(Lis, structural_user_list, root):
    retrieved_el_xml = []
    counter = 0
    condition = False
    list_provisoire = []
    length = len(structural_user_list) - 1
    #Managing data from first to second last one:
    for i in range(length):
        if isinstance(structural_user_list[i], str) or isinstance(structural_user_list[i], Attribute):
            if isinstance(structural_user_list[i + 1], list):
                #  manage first case of Ep1[Es1...]
                if structural_user_list[i] in Lis:
                    counter = len(list(root.iter(structural_user_list[i])))
                    # loop into the xml file
                    for child in root.findall(structural_user_list[i]):
                        condition = True
                        # managing the extension case [start_date,[Start_date,type]]
                        if counter <= 1 and len(structural_user_list[i + 1]) == 1 and structural_user_list[i + 1][0] == \
                                structural_user_list[
                                    i]:
                            list_provisoire.extend(main_search_v01(Lis, structural_user_list[i + 1], root))
                        elif counter > 1:
                            list_provisoire.append(main_search_v01(Lis, structural_user_list[i + 1], child))
                        else:
                            list_provisoire.extend(main_search_v01(Lis, structural_user_list[i + 1], child))
                    if condition == True and counter > 1:
                        retrieved_el_xml.append(list_provisoire)
                        list_provisoire = []
                    elif condition == True:
                        retrieved_el_xml.extend(list_provisoire)
                        list_provisoire = []
                    else:  # if StructuralUserList[i] not found
                        for i in range(counter_column(structural_user_list[i + 1], counter)):
                            retrieved_el_xml.append('')
                    condition = False
                # manage second case: Es1[Ess1,...]
                else:
                    counter = len(list(root.iter(structural_user_list[i])))
                    for child in root.iter(structural_user_list[i]):
                        condition = True
                        if counter > 1:
                            list_provisoire.append(main_search_v01(Lis, structural_user_list[i + 1], child))
                        else:
                            list_provisoire.extend(main_search_v01(Lis, structural_user_list[i + 1], child))
                    if condition == True and counter > 1:
                        retrieved_el_xml.append(list_provisoire)
                        list_provisoire = []
                    elif condition == True:
                        retrieved_el_xml.extend(list_provisoire)
                        list_provisoire = []
                    else:  # if StructuralUserList[i] not found
                        for i in range(counter_column(structural_user_list[i + 1], counter)):
                            retrieved_el_xml.append('')
                    condition = False
                    list_provisoire = []
            # manages these cases: Es1,Es2...
            elif isinstance(structural_user_list[i + 1], str) or isinstance(structural_user_list[i + 1], Attribute):
                if isinstance(structural_user_list[i], Attribute):
                    if structural_user_list[i].Name in root.attrib:
                        retrieved_el_xml.append(root.get(structural_user_list[i].Name))
                    else:
                        retrieved_el_xml.append('')
                # Case of several headers element in the root
                elif structural_user_list[i] in Lis and len(root.findall(structural_user_list[i])) > 1:
                    for children in root.findall(structural_user_list[i]):
                        list_one = []
                        list_one.append(children.text)
                        list_provisoire.append(list_one)
                    retrieved_el_xml.append(list_provisoire)
                    list_provisoire = []
                else:
                    for children in root.findall(structural_user_list[i]):
                        condition = True
                    if condition:
                        list_provisoire.append(children.text)
                    if not condition:
                        if structural_user_list[i] in root.tag and root.text is not None:
                            retrieved_el_xml.append(root.text)
                        else:
                            retrieved_el_xml.append('')
                    retrieved_el_xml.extend(list_provisoire)
                    list_provisoire = []
                    condition = False
    # if the last member is a string in Lis it will be omit by the function because of the use of i+1 so this
    # last section is dealing with the last element
    if isinstance(structural_user_list[length], str) or isinstance(structural_user_list[length], Attribute):
        if isinstance(structural_user_list[length], Attribute):
            if structural_user_list[length].Name in root.attrib:
                retrieved_el_xml.append(root.get(structural_user_list[length].Name))
            else:
                retrieved_el_xml.append('')
        else:
            for children in root.findall(structural_user_list[length]):
                condition = True
                list_one = []
                list_one.append(children.text)
                list_provisoire.append(list_one)
            if condition:
                retrieved_el_xml.append(list_provisoire)
            else:
                retrieved_el_xml.append('')
    return retrieved_el_xml

def check_in_list(List):
    dim = 0
    for element in List:
        if isinstance(element, str):
            dim += 1
        elif isinstance(element, list):
            dim = dim + check_in_list(element)
    return dim

def number_of_lines(List):
    list_count=[]
    counter = 0
    for i in range(len(List)):
        if isinstance(List[i], list):
            if check_in_list(List[i]) == len(List[i]):
                if (isinstance(e,list)==True for e in List[i]) :
                    counter = counter + number_of_lines(List[i])
                else:
                    counter += 1
            else:
                counter = counter + number_of_lines(List[i])
        else:
            counter = 1
        list_count.append(counter)
    return max(list_count)

# The Function goes into the List and create a list of the first elements in each sublists
# The list is always written as follow: [Ep1[[Es1[[Ess1,Ess2],[Ess3,Ess4]],[Es2,[[Ess1,Ess2],[Ess3,Ess4]]],Ep2...]

def parse_list_v01(List):
    one_row = []
    restes=List[:]
    for element in List:
        # solve the first element issue
        if isinstance(element, str):
            one_row.append(element)
            restes[restes.index(element)]=''
        elif isinstance(element, list):
            length=len(element)
            x, y = parse_list_v01(element[0])
            if length>1 and check_in_list(y) == len(y):
                restes[restes.index(element)].remove(element[0])
            elif length > 1 and check_in_list(y) != len(y):
                restes[restes.index(element)][0]=y
            elif check_in_list(y) != len(y) and length==1:
                restes[restes.index(element)][0]=y
            elif check_in_list(y) == len(y) and length==1:
                for sub in y:
                    restes.insert(restes.index(restes[restes.index(element)]), '')
                restes.remove(restes[restes.index(element)])
            one_row.extend(x)
    return one_row, restes
def write_all_rows_v01(List):
    all_rows = []
    counter = 0
    condition = True
    restes=[]
    while condition:
        counter += 1
        one_row,restes = parse_list_v01(List)
        List=restes
        all_rows.append(one_row)
        counter2 = 0
        for element in one_row:
            if element != '':
                counter2 += 1
        #if counter > 100:
            #break
        if counter2 == 0:
            condition = False
    all_rows.pop()
    return all_rows
# this function is optional, if you have different variables for one headers, it will gather the variables into one cell
# it enter write_all_rows function and out the single row.
# for instance, for the case of different countries, it will edit it as follow: mexico|USA|Canada
def single_row(List):
    single_row = []
    condition = False
    for element in List:
        if isinstance(element, list):
            condition = True
    if condition:
        for i in range(len(List[0])):
            list_prov = []
            for list_take in List:
                if list_take[i] != '':
                    list_prov.append(list_take[i])
            list_prov = list(dict.fromkeys(list_prov))
            if len(list_prov) > 1:
                list_prov = ' | '.join(list_prov)
            else:
                list_prov = ''.join(list_prov)
            single_row.append(list_prov)
    else:
        single_row.append(List)
    return single_row