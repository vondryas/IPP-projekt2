from . import ErrorHandler as e
# Class that implement semantic analysis of the code
class SemanticAnalyzer:

    __slots__ = ("labels", "error_message", "_expected_labels", "_frames", "force_exit")

    def __init__(self, force_exit=False):
        self.labels = {}
        self._expected_labels = []
        self.error_message = ""
        self._frames = ["GF", "LF", "TF"]
        self.force_exit = force_exit

    # Method that converts string to int
    @staticmethod
    def str_to_int(string: str):
        base = 10
        if string.lower().startswith('0x'):
            base = 16
        elif string.lower().startswith('0o'):
            base = 8
        return int(string, base)
    
    # Method that converts string to bool
    @staticmethod
    def to_bool(string: str):
        return True if string.upper() == "TRUE" else False

    # Method that add label to dict of labels
    # if label is already in dict of labels returns error code 52
    # if label is in list of expected labels removes it from list of expected labels
    def add_label(self, label, pc):
        if label in self.labels:
            self.error_message = f"Label {label} on index {pc} is already defined in line {self.labels[label]}. Indexed from 0"
            return 52
        if label in self._expected_labels:
            self._expected_labels.remove(label)

        self.labels[label] = pc
        return 0

    # Method that add to list of expected labels
    # if label is not in list of labels and not in list of expected labels
    def add_expected_label(self, label):
        if label not in self._expected_labels and label not in self.labels:
            self._expected_labels.append(label)

    # Method checks if arguments constants has same valid type at the same time
    # if not returns error code 53
    # if instuction is not EQ, JUMPIFEQ or JUMPIFNEQ and one of arguments is nil
    # returns error code 53
    # if instruction is EQ, JUMPIFEQ or JUMPIFNEQ and one of arguments is nil
    # returns 0
    def check_relation_operators_constants(self, instruction, code):
        type_1 = instruction[2].split("@",1)[0]
        type_2 = instruction[3].split("@",1)[0]
        valid_types = ["int", "string", "bool"]
        if type_1 not in self._frames and type_2 not in self._frames:
            if instruction[0] in ["EQ", "JUMPIFEQ", "JUMPIFNEQ"]:
                if type_1 == "nil" or type_2 == "nil":
                    return 0
            for type_ in valid_types:
                if (type_1 == type_ and type_2 == type_):
                    return 0
        else:
            if type_1 not in self._frames:
                if instruction[0] not in ["EQ", "JUMPIFEQ", "JUMPIFNEQ"]:
                    if type_1 == "nil":
                        self.error_message = f"Invalid type {type_1} of first argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0"
                        return 53
            if type_2 not in self._frames:
                if instruction[0] not in ["EQ", "JUMPIFEQ", "JUMPIFNEQ"]:
                    if type_2 == "nil":
                        self.error_message = f"Invalid type {type_2} of second argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0"
                        return 53
            return 0
        self.error_message = f"Invalid type {type_1} of first argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0"
        return 53

    # Method that checks if constant given in argument is valid for int2char.
    # if invalid type return 53
    # if invalid value return 58
    # if valid return 0
    def check_int2char(self, instruction, code):
        type_1, value = instruction[2].split("@",1)
        if type_1 not in self._frames:
            if type_1 != "int":
                self.error_message = f"Invalid type {type_1} of first argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nOnly int is allowed"
                return 53
            elif SemanticAnalyzer.str_to_int(value) < 0 or SemanticAnalyzer.str_to_int(value) > 0x10FFFF:
                self.error_message = f"Invalid value {value} of first argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nOnly <0 - 0x10FFFF> is allowed"
                return 58
        return 0
    
    # Method that checks if constant given in argument is valid for exit.
    # if invalid type return 53
    # if invalid value return 57
    # if valid return 0
    def check_exit(self, instruction, code):
        type_1, value = instruction[1].split("@",1)
        if type_1 not in self._frames:
            if type_1 != "int":
                self.error_message = f"Invalid type {type_1} of first argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nOnly int is allowed"
                return 53
            elif SemanticAnalyzer.str_to_int(value) < 0 or SemanticAnalyzer.str_to_int(value) > 49:
                self.error_message = f"Invalid value {value} of first argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nOnly <0 - 49> is allowed"
                return 57
        return 0

    # Method that checks if constant is valid for given valid types.
    # it can take 1 or 2 arguments it can be used for instructions that only check if 
    # constant in argument is valid input for given instruction
    # if not valid return 53 else 0
    def check_type_mul_operands(self, instruction, code, number_of_operands, first_type, second_type = None):
        if number_of_operands == 1:
            type_1 = instruction[2].split("@",1)[0]
        elif number_of_operands == 2:
            type_1, value1 = instruction[2].split("@",1)
            type_2, value2 = instruction[3].split("@",1)

        if type_1 not in self._frames:
            if type_1 != first_type:
                self.error_message = f"Invalid type {type_1} of first argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nOnly {first_type} is allowed"
                return 53
        if number_of_operands > 1:
            if type_2 not in self._frames:
                if type_2 != second_type:
                    self.error_message = f"Invalid type {type_2} of second argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nOnly {second_type} is allowed"
                    return 53
                if instruction[0] == "IDIV":
                    if SemanticAnalyzer.str_to_int(value2) == 0:
                        self.error_message = f"Invalid value {value2} of second argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nCannot divide by 0"
                        return 57
                if instruction[0] == "SETCHAR":
                    if len(value2) == 0:
                        self.error_message = f"Invalid value {value2} of second argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nEmpty string is not allowed"
                        return 58
                if instruction[0] in ["GETCHAR", "STRI2INT"]:
                    if  len(value1) == 0:
                        self.error_message = f"Invalid value {value2} of first argument in instruction {instruction[0]} on index {code.index(instruction)}. Indexed from 0\nEmpty string is not allowed"
                        return 58
        return 0


    # Method that do semantic analysis of given code.
    # Erro will be handled by decorator
    @e.ErrorHandler.handle_error
    def check_semantic(self, code, force_exit = False):
        # Reset
        self.__init__(force_exit=force_exit)
        # Checking for labels and adding them to self.labels
        # Checking constants and their types
        for instruction in code:
            if instruction[0] == "LABEL":
                if self.add_label(instruction[1], code.index(instruction)) != 0:
                    return 52
            elif instruction[0] in ["JUMP", "JUMPIFEQ", "JUMPIFNEQ", "CALL"]:
                self.add_expected_label(instruction[1])
                if instruction[0] in ["JUMPIFEQ", "JUMPIFNEQ"]:
                    err = self.check_relation_operators_constants(instruction, code)
                    if err != 0:
                        return err
            elif instruction[0] in ["ADD", "SUB", "MUL", "IDIV"]:
                err = self.check_type_mul_operands(instruction, code, 2, "int", "int")
                if err != 0:
                    return err
            elif instruction[0] in ["LT", "GT", "EQ"]:
                err = self.check_relation_operators_constants(instruction, code)
                if err != 0:
                    return err
            elif instruction[0] in ["AND", "OR"]:
                err = self.check_type_mul_operands(instruction, code, 2, "bool", "bool")
                if err != 0:
                    return err
            elif instruction[0] == "NOT":
                err = self.check_type_mul_operands(instruction, code, 1, "bool")
                if err != 0:
                    return err
            elif instruction[0] == "INT2CHAR":
                err = self.check_int2char(instruction, code)
                if err != 0:
                    return err
            elif instruction[0] == "STRI2INT":
                err = self.check_type_mul_operands(instruction, code, 2, "string", "int")
                if err != 0:
                    return err
            elif instruction[0] == "CONCAT":
                err = self.check_type_mul_operands(instruction, code, 2, "string", "string")
                if err != 0:
                    return err
            elif instruction[0] == "STRLEN":
                err = self.check_type_mul_operands(instruction, code, 1, "string")
                if err != 0:
                    return err
            elif instruction[0] == "GETCHAR":
                err = self.check_type_mul_operands(instruction, code, 2, "string", "int")
                if err != 0:
                    return err
            elif instruction[0] == "SETCHAR":
                err = self.check_type_mul_operands(instruction, code, 2, "int", "string") 
                if err != 0:
                    return err
            elif instruction[0] == "EXIT":
                err = self.check_exit(instruction, code)
                if err != 0:
                    return err

        # Check if all labels are defined
        if self._expected_labels:
            self.error_message = f"Labels {self._expected_labels} are not defined"
            return 52

        return 0
