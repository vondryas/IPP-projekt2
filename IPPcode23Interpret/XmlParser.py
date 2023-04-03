import re
import xml.dom.minidom as mdom
import sys

class XmlParser:

    __slots__ = ("code", "TYPES", "error_message")

    def __init__(self):
        self.code = []
        self.TYPES = ["int", "bool", "string", "nil"]
        self.error_message = ""

    @staticmethod
    def to_string(string):
        return re.sub(r'\\(\d{3})', lambda match: chr(int(match.group(1))), string)

    def parse_to_interpreter(self, xml_file = None):
        try:
            if xml_file is not None:
                dom = mdom.parse(xml_file)
            else:
                dom = mdom.parseString(sys.stdin.read())
        except Exception:
            self.error_message = f"XML file {xml_file} is not well-formed"
            return 31

        try:
            self.code = []
            program = dom.documentElement
            instructions = program.getElementsByTagName("instruction")
            for instruction in instructions:
                instruction_node = []
                order = instruction.getAttribute("order")
                instruction_node.append(order)
                opcode = instruction.getAttribute("opcode")
                instruction_node.append(opcode)
                for i in range(1, 4):
                    argument = instruction.getElementsByTagName(f"arg{i}")
                    if argument:
                        type_ = argument[0].getAttribute("type")
                        if type_ in self.TYPES:
                            string = argument[0].firstChild.data if argument[0].firstChild is not None else ""
                            if type_ == "string":
                                string = XmlParser.to_string(string)
                            arg = type_ + "@" + string
                        else:
                            arg = argument[0].firstChild.data
                        instruction_node.append(arg)
                self.code.append(instruction_node)
        except Exception:
            self.error_message = f"XML file {xml_file} have wrong structure"
            return 32
        self.code = sorted(self.code, key=lambda x: int(x[0]))
        self.code = [instruction[1:] for instruction in self.code]
        return 0
