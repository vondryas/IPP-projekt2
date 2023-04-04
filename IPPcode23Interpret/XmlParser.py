import re
import xml
import xml.dom.minidom as mdom
import sys

# Class for parsing xml file to list of instructions
class XmlParser:

    __slots__ = ("code", "TYPES", "error_message")

    def __init__(self):
        self.code = []
        self.TYPES = ["int", "bool", "string", "nil"]
        self.error_message = ""

    # Convert escape sequences to characters
    @staticmethod
    def escape_seq_to_char(string):
        return re.sub(r'\\(\d{3})', lambda match: chr(int(match.group(1))), string)
    
    # Check if program element is valid
    def check_program_element(self, root):
        root_att = list(root.attributes.keys())
        valid_attr = ["language", "name", "description"]

        if root.tagName != "program":
            self.error_message = f"Root element must have name 'program' not {root.tagName}.\nXML file have wrong structure"
            return 32  
        
        for attribute_name in root_att:
            if attribute_name not in valid_attr:
                self.error_message = f"Root element has invalid attribute {attribute_name}.\nXML file have wrong structure"
                return 32
            else:
                valid_attr.remove(attribute_name)
        
        if "language" in valid_attr:
            self.error_message = f"Root element has no attribute language.\nXML file have wrong structure"
            return 32
        
        if root.getAttribute("language").lower() != "ippcode23":
            self.error_message = f"Root attribute language must have value IPPcode23 not {root.getAttribute('language')}.\nXML file have wrong structure"
            return 32
        
        return 0
    
    # Check if there are only instruction elements in program element
    def check_instructions_level_structure(self, program):
        for elem in program.childNodes:
            if elem.nodeType == elem.ELEMENT_NODE:
                if elem.tagName != "instruction":
                    self.error_message = f"Element {elem.tagName} cannot be in a place where only element instruction can be.\nXML file have wrong structure"
                    return 32
        return 0

    # Check if instruction element is valid and there are only argument elements in instruction element
    # And if order is unique
    # Returning order of instruction
    def check_instruction_element(self, instruction, order_list):
        instruction_att = list(instruction.attributes.keys())
        valid_attr = ["order", "opcode"]
        valid_elem = ["arg1", "arg2", "arg3"]

        for attribute_name in instruction_att:
            if attribute_name in valid_attr:
                valid_attr.remove(attribute_name)
            else:
                self.error_message = f"Instruction element has invalid attribute {attribute_name}.\nXML file have wrong structure"

        if valid_attr:
            self.error_message = f"Instruction element has no attributes {valid_attr}.\nXML file have wrong structure"
        
        order = instruction.getAttribute("order")

        if not order.isdigit():
            self.error_message = f"Instruction attribute order must be a number not {instruction.getAttribute('order')}.\nXML file have wrong structure"

        order = int(order)

        if order in order_list:
            self.error_message = f"Instruction attribute order must be unique number. Conflict number {order}\nXML file have wrong structure"
        
        for argument in instruction.childNodes:
            if argument.nodeType == argument.ELEMENT_NODE:
                if argument.tagName not in valid_elem:
                    self.error_message = f"Invalid or duplicite element {argument.tagName}.\nXML file have wrong structure"
                else:
                    valid_elem.remove(argument.tagName)

        return order

    # Check if argument element is valid
    def check_argument_element(self, argument):
        arg_att = list(argument.attributes.keys())
        if len(arg_att) != 1:
            self.error_message = f"Argument element has invalid number of attributes.\nXML file have wrong structure"
            return 32
        if arg_att[0] != "type":
            self.error_message = f"Argument element has invalid attribute {arg_att[0]}. Only attribute \"type\" is allowed.\nXML file have wrong structure"
            return 32
        if len(argument.childNodes) > 1:
            self.error_message = f"Argument element has invalid number of child elements.\nXML file have wrong structure"
            return 32
        return 0

    def parse_to_interpreter(self, xml_file = None):
        # Parse XML file
        try:
            if xml_file is not None:
                dom = mdom.parse(xml_file)
            else:
                dom = mdom.parseString(sys.stdin.read())

        except xml.parsers.expat.ExpatError:
            self.error_message = f"XML file {xml_file} is not well-formed"
            return 31

        # Creating list of instructions for interpreter
        self.code = []

        # Root "program" element
        program = dom.documentElement

        # Checking root and instruction elements structure
        if self.check_program_element(program) != 0:
            return 32
        if self.check_instructions_level_structure(program) != 0:
            return 32

        # List of instructions
        instructions = program.getElementsByTagName("instruction")
        
        # List of order numbers
        order_list = []
        for instruction in instructions:
            
            # Creating instruction node
            instruction_node = []

            # Checking instruction and argument elements structure
            order = self.check_instruction_element(instruction, order_list)

            # Check if there is an error from previous function
            if self.error_message != "":
                return 32

            # Adding order number to list
            order_list.append(order)
            # Adding order number to instruction node
            instruction_node.append(order)

            
            # Adding opcode to instruction node
            opcode = instruction.getAttribute("opcode")
            instruction_node.append(opcode.upper().strip())

            # Boolean for checking if there is an error with sequence of arguments
            # for example: <arg3> <arg2>
            # or: <arg1> <arg3>
            arguments_sequence_err = False

            # Checking arguments 
            for i in range(1, 4):
                argument = instruction.getElementsByTagName(f"arg{i}")
                if argument:
                    
                    # Error if wrong sequence of arguments
                    if arguments_sequence_err:
                        self.error_message = "Instruction element has invalid sequence of arguments.\nXML file have wrong structure"
                        return 32
                    
                    # Checking argument element structure
                    if self.check_argument_element(argument[0]) != 0:
                        return 32

                    type_ = argument[0].getAttribute("type").lower().strip()
                    # If there must be type@value for interpeter
                    if type_ in self.TYPES:

                        value= argument[0].firstChild.data if argument[0].firstChild is not None else ""
                        # If type is string, it convert escape sequences to characters
                        value = value.strip()
                        if type_ == "string":
                            value = XmlParser.escape_seq_to_char(value)

                        arg = type_ + "@" + value

                    else:
                        arg = argument[0].firstChild.data.strip() if argument[0].firstChild is not None else ""

                    # Adding argument to instruction node
                    instruction_node.append(arg)
                # If there shouldnt be next argument
                else:
                    arguments_sequence_err = True

            # Adding instruction node to list of instructions for interpreter
            self.code.append(instruction_node)

        # Sorting instructions by order number
        self.code = sorted(self.code, key=lambda x: int(x[0]))

        # Removing order numbers from instructions
        self.code = [instruction[1:] for instruction in self.code]
        return 0
