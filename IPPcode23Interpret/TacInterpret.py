import sys
from . import Nil
from . import ErrorHandler as e
# Custom exceptions that are used in interpreter
# They take instance of object and message as arguments
# message will be stored in error_message attribute of object
# code is used for returning error code from interpret.py
class RedefiningVariable(Exception):

    def __init__(self, this, message):
        super().__init__(message)
        this.error_message = message
        self.code = 52


class BadOperandTypes(Exception):

    def __init__(self, this, message):
        super().__init__(message)
        this.error_message = message
        self.code = 53


class NotExistingVariable(Exception):

    def __init__(self, this, message):
        super().__init__(message)
        this.error_message = message
        self.code = 54


class NotExistingFrame(Exception):

    def __init__(self, this, message):
        super().__init__(message)
        this.error_message = message
        self.code = 55


class MissingOperandValue(Exception):

    def __init__(self, this, message):
        super().__init__(message)
        this.error_message = message
        self.code = 56


class BadOperandValue(Exception):

    def __init__(self, this, message):
        super().__init__(message)
        this.error_message = message
        self.code = 57


class StringError(Exception):

    def __init__(self, this, message):
        super().__init__(message)
        this.error_message = message
        self.code = 58

# Class that contains init method for iterpret data
# It also contains all attributes that are used in interpret
# It is used in all parts of interpret
class InterpretData:

    _slots__ = ("_code", "_labels", "_pc",
                "_global_frame", "_local_frames",
                "_temporary_frame", "_call_stack",
                "_data_stack", "FRAMES", "TYPES",
                "error_message", "_instruction_count"
                "_input_stream", "force_exit")

    def __init__(self, code: list, labels: dict, input_stream=sys.stdin, force_exit=False):
        #                                                               0       1      2     3
        # code is list of instructions  instruction is in format [instruction, arg1, arg2, arg3]
        # active instruction: self.code[self._pc][0]
        # argument 1: self.code[self._pc][1]
        # argument 2: self.code[self._pc][2]
        # argument 3: self.code[self._pc][3]
        self.code = code
        # labels are stored in dictionary 
        self._labels = labels
        # program counter is poiter to current instruction
        self._pc = 0
        # frames are dictionaries that store variables
        self._global_frame = {}
        # local frames are stored as stack of dictionaries
        self._local_frames = []
        # temporary frame is dictionary
        self._temporary_frame = None
        # call stack is stack of program counters
        self._call_stack = []
        # data stack is stack of values
        self._data_stack = []

        # Number of executed instructions
        self._instruction_count = 0
        # Dictionary that contains all frame names and their attributes
        self.FRAMES = {"GF": self._global_frame,
                       "LF": self._local_frames, "TF": self._temporary_frame}
        # Dictionary that contains all types and their conversion methods
        self.TYPES = {"int": ExecuterUtils.str_to_int, "string": str,
                      "bool": ExecuterUtils.to_bool, "nil": Nil.nil}
        # Input stream is used for reading from file or stdin
        self._input_stream = sys.stdin if input_stream is None else input_stream
        # Error message is used for storing error message
        self.error_message = ""
        # Force exit is used for exiting interpret
        self.force_exit = force_exit

# Class containing all helper methods for Executer class
# It is specific for work with InterpretData class
class ExecuterUtils(InterpretData):

    __slots__ = ()

    # Method that is used as decorator for all methods that
    # want to return Exception as error code if error occurs
    def return_err_code_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RedefiningVariable as e:
                return e.code
            except BadOperandTypes as e:
                return e.code
            except NotExistingVariable as e:
                return e.code
            except NotExistingFrame as e:
                return e.code
            except MissingOperandValue as e:
                return e.code
            except BadOperandValue as e:
                return e.code
            except StringError as e:
                return e.code
        return wrapper

    # Method that is used as decorator for all methods that
    # want to raise Exception to another function if error occurs
    def raise_again_err_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RedefiningVariable as e:
                raise e
            except BadOperandTypes as e:
                raise e
            except NotExistingVariable as e:
                raise e
            except NotExistingFrame as e:
                raise e
            except MissingOperandValue as e:
                raise e
            except BadOperandValue as e:
                raise e
            except StringError as e:
                raise e
        return wrapper

    # Method that is used as decorator for all methods that
    # want to be counted as instruction
    def instruction(func):
        setattr(func, "Instruction", True)
        return func

    
    # Method that is used as decorator for all methods that
    # will write true or false if method hase instruction decorator
    def is_instruction(func):
        return hasattr(func, "Instruction")

    # Method that converts string to int
    @staticmethod
    def str_to_int(string: str):
        base = 10
        if string.lower().startswith('0x') or string.lower().startswith('+0x') or string.lower().startswith('-0x'):
            base = 16
        elif string.lower().startswith('0o') or string.lower().startswith('+0o') or string.lower().startswith('-0o'):
            base = 8

        return int(string, base)


    # Method that converts string to bool
    @staticmethod
    def to_bool(string: str):
        return True if string.upper() == "TRUE" else False
    
    # Method that converts bool to string
    @staticmethod
    def from_bool(boolean: bool):
        return "true" if boolean else "false"

    # Methods that return splited arguments of "type/frame@value/name" format
    def parse_sym(self):
        frame, var_name = self.code[self._pc][1].split("@", 1)
        return frame, var_name

    def parse_2sym(self):
        first, second = self.code[self._pc][1].split("@", 1)
        third, fourth = self.code[self._pc][2].split("@", 1)
        return first, second, third, fourth

    def parse_3sym(self):
        first, second = self.code[self._pc][1].split("@", 1)
        third, fourth = self.code[self._pc][2].split("@", 1)
        fifth, sixth = self.code[self._pc][3].split("@", 1)
        return first, second, third, fourth, fifth, sixth

    def parse_lab_2sym(self):
        first, second = self.code[self._pc][2].split("@", 1)
        third, fourth = self.code[self._pc][3].split("@", 1)
        return first, second, third, fourth

    # Method that returns top frame of local frames
    # Or only return frame if it is not list
    # Raises exception if local frames is empty
    def top_frame(self, lst):
        if type(lst) == list:
            try:
                lst = lst[-1]

            except IndexError:
                raise NotExistingFrame(self, f"No local frame when calling instruction {self.code[self._pc][0]} in program counter: {self._pc}.")
            
        if lst is None:
            raise NotExistingFrame(self, f"No temporary frame when calling instruction {self.code[self._pc][0]} in program counter: {self._pc}.")
        
        return lst

    # Method that returns value of symbol
    # Raises exception if variable is not defined
    # Raises exception if variable is not defined in frame
    # Because of decorator it raises exception if some of the methods
    # that are called in this method raises exception
    @raise_again_err_decorator
    def get_sym_value(self, frame_or_sym, type_key, value_key, none_check=True):
        if frame_or_sym:
            try:
                # Frame
                value = ExecuterUtils.top_frame(
                    self, self.FRAMES[type_key])[value_key]
                # Check if variable is initialized
                if none_check and value is None:
                    raise MissingOperandValue(
                        self, f"Variable {type_key}@{value_key} not initialized. Instruction {self.code[self._pc][0]} on program counter: {self._pc}")
                
                return value
            
            except KeyError:
                raise NotExistingVariable(
                    self, f"No variable {type_key}@{value_key} in frame when calling instruction {self.code[self._pc][0]} in program counter: {self._pc}.")
        else:
            # Sym
            return self.TYPES[type_key](value_key)
    
    # Method that sets value of variable
    # Raises exception if variable is not defined in frame
    # Because of decorator it raises exception if some of the methods
    # that are called in this method raises exception
    @raise_again_err_decorator
    def set_var_value(self, frame_type_key, value_key, value_to_set):
            frame = ExecuterUtils.top_frame(self, self.FRAMES[frame_type_key])

            if value_key not in frame and value_to_set is not None:
                raise NotExistingVariable(
                    self, f"No variable {frame_type_key}@{value_key} in frame when calling instruction {self.code[self._pc][0]} in program counter: {self._pc}.")
            
            frame[value_key] = value_to_set
            

    # Method that will do calculations for arithmetic, relational and logical instructions
    # Arguments: operation, valid_types, mode (optional) -> operation is function that will be used for calculation
    # valid_types is list of valid types for operands
    # Raises exception if operand types are not valid
    # Raises exception if operand values are not valid for operation that has mode "div" (division by zero)
    # Because of decorator it raises exception if some of the methods
    # that are called in this method raises exception
    @raise_again_err_decorator
    def calculation(self, operation, valid_types, mode=""):
        if "not" == mode:
            frame, var_name, frame_sym1, name_sym1 = ExecuterUtils.parse_2sym(
                self)
        else:
            frame, var_name, frame_sym1, name_sym1, frame_sym2, name_sym2 = ExecuterUtils.parse_3sym(
                self)

        first_value = ExecuterUtils.get_sym_value(
            self, frame_sym1 in self.FRAMES, frame_sym1, name_sym1)
        
        # Not have only one operand so we need to check if it is not
        if not "not" == mode:
            second_value = ExecuterUtils.get_sym_value(
                self, frame_sym2 in self.FRAMES, frame_sym2, name_sym2)
        # If it is not then we need to check if operand type is bool
        else:
            if type(first_value) == bool:
                ExecuterUtils.set_var_value(
                    self, frame, var_name, (not first_value))
                return 0
            else:
                raise BadOperandTypes(
                    self, f"Invalid operand type in program counter: {self._pc} on instruction {self.code[self._pc][0]}")


        if "eq" == mode and (type(first_value) == Nil.nil or type(second_value) == Nil.nil):
            ## Set variable to output of comparison
            ExecuterUtils.set_var_value(
                self, frame, var_name, (first_value == second_value))
            
            return 0

        if "div" == mode and second_value == 0:
            BadOperandValue(
                self, f"Division by zero in program counter: {self._pc}")

        for _type in valid_types:
            if type(first_value) == _type and type(second_value) == _type:
                # Set variable to output of operation given as argument to this method
                ExecuterUtils.set_var_value(
                    self, frame, var_name, operation(first_value, second_value))
                
                return 0

        raise BadOperandTypes(
            self, f"Invalid operand types in program counter: {self._pc} on instruction {self.code[self._pc][0]}")

# Class that have methods that implements three address code instructions
class Executer(ExecuterUtils, InterpretData):

    __slots__ = ()

    # Because of decorator all methods return exception error code if some of the methods
    # that are called in this method raises exception

    # Method that implements instruction MOVE (move value from second argument to variable in first argument)
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def move(self):
        # Parse variable or constant
        dest_frame, dest_var_name, src_frame, src_var_name = Executer.parse_2sym(
            self)
        # Get value from second argument of MOVE
        src_value = Executer.get_sym_value(
            self, src_frame in self.FRAMES, src_frame, src_var_name)
        # Store value in variable in first argument of MOVE
        Executer.set_var_value(self, dest_frame, dest_var_name, src_value)
        return 0

    # Method that implements instruction CREATEFRAME (create new temporary frame)
    # Overwrites temporary frame if it already exists
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def create_frame(self):
        self._temporary_frame = {}
        self.FRAMES["TF"] = self._temporary_frame
        return 0

    # Method that implements instruction PUSHFRAME (push temporary frame to local frames)
    # It will push to local frames stack and set temporary frame to None
    # Raises exception if temporary frame before pushing is None
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def push_frame(self):
        if self._temporary_frame == None:
            raise NotExistingFrame(
                self, f"Missing frame in program counter: {self._pc} in instruction {self.code[self._pc][0]}")
        
        else:
            self._local_frames.append(self._temporary_frame)
            self._temporary_frame = None
            self.FRAMES["TF"] = self._temporary_frame
            return 0

    # Method that implements instruction POPFRAME (pop frame from local frames to temporary frame)
    # It will redefine current temporary frame by popped frame
    # Raises exception if local frames stack is empty
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def pop_frame(self):
        # if _local_frames stack is empty
        if not self._local_frames:
            raise NotExistingFrame(
                self, f"Missing frame in program counter: {self._pc} in instruction {self.code[self._pc][0]}")
        else:
            self._temporary_frame = self._local_frames.pop()
            self.FRAMES["TF"] = self._temporary_frame
            return 0

    # Method that implements instruction DEFVAR (define variable in frame)
    # After defining variable it will be set to None which is not initialized value
    # Raises exception if variable is already defined in frame
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def def_var(self):
        frame, var_name = Executer.parse_sym(self)
        # If variable is in given frame raise exception
        if var_name in Executer.top_frame(self, self.FRAMES[frame]):
            raise RedefiningVariable(
                self, f"Variable {frame}@{var_name} redefining on program counter {self._pc}.")
        
        Executer.set_var_value(self, frame, var_name, None)
        return 0

    # Method that implements instruction CALL (call function)
    # Add to call stack current program counter and set program counter to pc of label in argument
    # It is done by dict of labels
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def call(self):
        self._call_stack.append(self._pc)
        self._pc = self._labels[self.code[self._pc][1]]
        return 0

    # Method that implements instruction RETURN (return from function)
    # Set interpret program counter to poped value from call stack
    # Raises exception if call stack is empty
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _return(self):
        if not self._call_stack:
            raise MissingOperandValue(
                    self, f"Missing return value in program counter: {self._pc}")
            
        else:
            self._pc = self._call_stack.pop()
            return 0

    # Method that implements instruction PUSHS (push value to data stack)
    # add to data stack value from symbol in argument
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def pushs(self):
        frame, var_name = Executer.parse_sym(self)
        # Get value from symbol
        value = Executer.get_sym_value(
                    self, frame in self.FRAMES, frame, var_name)
        # Push value to data stack
        self._data_stack.append(value)
        return 0

    # Method that implements instruction POPS (pop value from data stack)
    # Store value from data stack to variable in argument
    # Raises exception if data stack is empty
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def pops(self):
        frame, var_name = Executer.parse_sym(self)
        # If data stack is empty raise exception
        if not self._data_stack:
            return 56
        
        else:
            Executer.set_var_value(
                self, frame, var_name, self._data_stack.pop())
            return 0

    # Methods that implements arithmetic instructions, logical instructions and relational instructions
    # Calling method calculation that implements all of them
    # It takes 3 arguments:
    #   - self
    #   - lambda function that implements instruction
    #   - list of types that are allowed in operands
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def add(self):
        return Executer.calculation(self, lambda x, y: x + y, [int])

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def sub(self):
        return Executer.calculation(self, lambda x, y: x - y, [int])

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def mul(self):
        return Executer.calculation(self, lambda x, y: x * y, [int])

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def idiv(self):
        return Executer.calculation(self, lambda x, y: x // y, [int], "div")

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def lt(self):
        return Executer.calculation(self, lambda x, y: x < y, [int, bool, str])

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def gt(self):
        return Executer.calculation(self, lambda x, y: x > y, [int, bool, str])

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def eq(self):
        return Executer.calculation(self, lambda x, y: x == y, [int, bool, str, Nil.nil], "eq")

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _and(self):
        return Executer.calculation(self, lambda x, y: x and y, [bool])

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _or(self):
        return Executer.calculation(self, lambda x, y: x or y, [bool])

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _not(self):
        return Executer.calculation(self, lambda x, y: not x, [bool], "not")

    # Method that implements instruction INT2CHAR (convert int to char)
    # Set converted char (argument 2) to variable (argument 1)
    # Raises exception if value is not int or value is not in range of unicode table
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def int2char(self):
        var_frame, var_name, sym_frame, sym_name = Executer.parse_2sym(self)
        # Get value from symbol
        value = Executer.get_sym_value(
            self, sym_frame in self.FRAMES, sym_frame, sym_name)
        
        # If value is not int raise exception
        if type(value) != int:
            raise BadOperandTypes(
                self, f"Invalid operand type for int2char: {type(value)} on program counter {self._pc}.\nOnly int is allowed.")
        # If value is out of range of unicode table raise exception    
        elif value < 0 or value > 0x10FFFF:
            raise StringError(
                self, f"Invalid value for int2char: {value} on program counter {self._pc}.\nOnly values from range 0-0x10FFFF are allowed.")
        
        # Convert value to char
        value = chr(value)
        
        # Set converted value to variable
        Executer.set_var_value(self, var_frame, var_name, value)
        return 0

    # Method that implements instruction STRI2INT (convert char to int)
    # Set converted int to variable in argument (argument 1)
    # Convert char from string (argument 2) on index (argument 3)
    # Raises exception if value is not string or index is not int
    # Raises exception if string is out of index
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def stri2int(self):
        var_frame, var_name, sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_3sym(self)
        # Get string from symbol
        value = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        # Get index from symbol
        index = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        # Type check
        if type(value) != str:
            raise BadOperandTypes(
                self, f"Invalid second operand type for str2int: {type(value)} on program counter {self._pc}.")
        
        if type(index) != int:
            raise BadOperandTypes(
                self, f"Invalid third operand type for str2int: {type(index)} on program counter {self._pc}.")

        # Convert char to int
        if index < len(value) and index >= 0:
            value = ord(value[index])
        # If string is out of index raise exception
        else:
            raise StringError(
                self, f"Invalid index for str2int: {index} on program counter {self._pc}.")



        Executer.set_var_value(
            self, var_frame, var_name, value)
        return 0
    
    # Method that implements instruction READ (read value from stdin or from file)
    # Set read value to variable (argument 1)
    # if value cannot be conveted to types (argument 2), set to nil
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def read(self):
        frame, var_name = Executer.parse_sym(self)
        try:
            input_ = self._input_stream.readline()
            if input_ == "":
                value = Nil.nil(None)
            else:
                value = self.TYPES[self.code[self._pc][2]](input_.rstrip("\n").rstrip("\r"))

        except ValueError:
            value = Nil.nil(None)

        Executer.set_var_value(self, frame, var_name, value)
        return 0

    # Method that implements instruction WRITE (write value to stdout or to file)
    # It writes value from first argument
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def write(self):
        frame, var_name = ExecuterUtils.parse_sym(self)

        value = Executer.get_sym_value(
            self, frame in self.FRAMES, frame, var_name)
        
        if type(value) == bool:
            print(ExecuterUtils.from_bool(value), end="")

        else:
            print(value, end="")
        return 0

    # Method that implements instruction CONCAT (concatenate strings)
    # Set concatenated string to variable in argument
    # It concatenates strings from second and third symbol
    # Raises exception if second and third symbol is not string
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def concat(self):
        var_frame, var_name, sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_3sym(self)

        value1 = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        
        value2 = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        
        if type(value1) != str or type(value2) != str:
            raise BadOperandTypes(
                self, f"Invalid operand types for concat: {type(value1)} and {type(value2)} on program counter {self._pc}.")
        # Concatenate strings
        value = value1 + value2

        Executer.set_var_value(self, var_frame, var_name, value)
        return 0

    # Method that implements instruction STRLEN (get length of string)
    # Set length of string to variable in argument
    # It gets length of string from second symbol
    # Raises exception if second symbol is not string
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def strlen(self):
        var_frame, var_name, sym_frame, sym_name = Executer.parse_2sym(self)

        value = Executer.get_sym_value(
            self, sym_frame in self.FRAMES, sym_frame, sym_name)
        
        if type(value) != str:
            raise BadOperandTypes(
                self, f"Invalid operand type for strlen: {type(value)} on program counter {self._pc}.")
        
        value = len(value)

        Executer.set_var_value(self, var_frame, var_name, value)
        return 0

    # Method that implements instruction GETCHAR (get char from string)
    # Set one char string to variable in argument
    # It gets char from string from second symbol and index from third symbol
    # Raises exception if string is out of index
    # Raises exception if value is not string or index is not int
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def get_char(self):
        var_frame, var_name, sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_3sym(
            self)
        string = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        index = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        if type(string) != str or type(index) != int:
            raise BadOperandTypes(
                self, f"Invalid operand type for get_char: {type(string)} and {type(index)} on program counter {self._pc}.")
        
        elif index >= len(string) or index < 0:
            raise StringError(
                self, f"Invalid index for get_char: {index} on program counter {self._pc}.")
        
        value = string[index]

        Executer.set_var_value(self, var_frame, var_name, value)
        return 0

    # Method that implements instruction SETCHAR (modify char in string)
    # Set modified string to variable (argument 1)
    # It gets string from first symbol (argument 1), index from second symbol (argument 2) and char from third symbol (argument 3)
    # Raises exception if char that is trying to be set is empty string
    # Raises exception if char that is trying to be set is not string or index is not int and variable is not string
    # Raises exception if string is out of index
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def set_char(self):
        var_frame, var_name, sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_3sym(self)
        
        string = Executer.get_sym_value(
            self, var_frame in self.FRAMES, var_frame, var_name)
        
        index = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        
        value = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        
        if type(string) != str or type(index) != int or type(value) != str:
            raise BadOperandTypes(
                self, f"Invalid operand type for set_char: {type(string)}, {type(index)} and {type(value)} on program counter {self._pc}.\nShould be string, int and string.")
        
        if index >= len(string) or index < 0:
            raise StringError(
                self, f"Invalid index for set_char: {index} on program counter {self._pc}.")
        
        if value == "":
            raise StringError(
                self, f"Invalid epmty string third argument in instruction {self.code[self._pc][0]} on program counter {self._pc}.")


        # modify string
        string = string[:index] + value[0] + string[index + 1:]
        
            
        # set modified string to variable
        Executer.set_var_value(self, var_frame, var_name, string)
        return 0

    # Method that implements instruction TYPE (get type of variable)
    # Set type of variable to variable in argument
    # It gets type of variable from second symbol
    # If variable is not defined, type is empty string
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _type(self):
        var_frame, var_name, sym_frame, sym_name = Executer.parse_2sym(self)

        value = Executer.get_sym_value(
            self, sym_frame in self.FRAMES, sym_frame, sym_name, False)
        
        if value is None:
            type_ = ""

        else:
            if isinstance(value, str):
                type_ = "string"
            else:
                type_ = type(value).__name__
        
        Executer.set_var_value(self, var_frame, var_name, type_)
        return 0

    # Method that implements instruction LABEL (set label)
    # its just a placeholder
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def label(self):
        return 0

    # Method that implements instruction JUMP (jump to label)
    # Set program counter to label
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def jump(self):
        self._pc = self._labels[self.code[self._pc][1]]
        return 0

    # Method that implements instruction JUMPIFEQ (jump to label if values equal)
    # Set program counter to label if values are equal
    # It gets values from second and third symbol
    # Raises exception if values are not same type. If one of the is nil it is ok
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def jump_if_eq(self):
        sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_lab_2sym(self)

        value1 = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        
        value2 = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        
        for type_ in [int, str, bool]:
            if (type(value1) == type_ and type(value2) == type_) or (type(value1) == Nil.nil or type(value2) == Nil.nil):
                # if eq it set program counter to label
                if value1 == value2:
                    self._pc = self._labels[self.code[self._pc][1]]
                return 0
            
        raise BadOperandTypes(
            self, f"Invalid operand types for jump_if_eq: {type(value1)} and {type(value2)} on program counter {self._pc}.")

    # Method that implements instruction JUMPIFNEQ (jump to label if values not equal)
    # does the opposite of jump_if_eq
    # Raises exception if values are not same type. If one of the is nil it is ok
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def jump_if_n_eq(self):
        sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_lab_2sym(self)

        value1 = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        
        value2 = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        
        for type_ in [int, str, bool]:
            if (type(value1) == type_ and type(value2) == type_) or (type(value1) == Nil.nil or type(value2) == Nil.nil):
                # if not eq it set program counter to label
                if value1 != value2:
                    self._pc = self._labels[self.code[self._pc][1]]
                return 0
            
        raise BadOperandTypes(
            self, f"Invalid operand types for jump_if_n_eq: {type(value1)} and {type(value2)} on program counter {self._pc}.")

    # Method that implements instruction EXIT (exit program)
    # Set exit code to value of symbol
    # Raises exception if value is not int or is not in range 0-49
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _exit(self):
        sym_frame, sym_name = Executer.parse_sym(self)

        value = Executer.get_sym_value(
            self, sym_frame in self.FRAMES, sym_frame, sym_name)
        
        if type(value) != int:
            raise BadOperandTypes(
                self, f"Invalid operand type for exit: {type(value)} on program counter {self._pc}.")
        
        if value < 0 or value > 49:
            raise BadOperandValue(
                self, f"Invalid exit code: {value} on program counter {self._pc}.")
        
        return value

    # Method that implements instruction DPRINT (print value of symbol to stderr)
    # Print value of symbol to stderr
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def d_print(self):
        sym_frame, sym_name = Executer.parse_sym(self)

        value = Executer.get_sym_value(
            self, sym_frame in self.FRAMES, sym_frame, sym_name)
        
        print(value, file=sys.stderr)
        return 0

    # Method that implements instruction BREAK (debugging tool)
    # Print all important information about current state of program to stderr
    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _break(self):
        print(
            f"previous instruction: {self.code[self._pc-1] if len(self.code) > 1  else self.code[self._pc]}", file=sys.stderr)
        print(f"current code: {self.code[self._pc]}", file=sys.stderr)
        print(
            f"current program counter (indexed from 0): {self._pc}", file=sys.stderr)
        print(
            f"instructions executed: {self._instruction_count}", file=sys.stderr)
        print(f"global frame: {self._global_frame}", file=sys.stderr)
        print(f"temporary frame: {self._temporary_frame}", file=sys.stderr)
        print("(top of stack is at the bottom of the list)", file=sys.stderr)
        print(f"local frames: {self._local_frames}", file=sys.stderr)
        print(f"call stack: {self._call_stack}", file=sys.stderr)
        print(f"data stack: {self._data_stack}", file=sys.stderr)
        return 0

    # Most important part. The dictionary that maps instruction names to their methods
    INSTRUCTIONS = {method_name.replace("_", "").upper(): method
                    for (method_name, method) in locals().items()
                    if ExecuterUtils.is_instruction(method)}

# Class that interprets the code
class TACInterpreter(Executer, InterpretData):

    __slots__ = ()

    def __init__(self, code: list = None, labels: dict = None, input_stream = sys.stdin, force_exit=False):
        InterpretData.__init__(self, code, labels, input_stream, force_exit)

    # Method that resets the interpreter to initial state 
    # Only with the code and labels that were provided in the constructor
    def reset(self, force_exit=False):
        self.__init__(self.code, self._labels, self._input_stream, force_exit)
    
    # Method that updates the code and labels
    def update_code(self, code, labels):
        if code != self.code:
            self.code = code
            self._labels = labels
    
    # Method that updates the input stream
    def update_input_stream(self, input_stream):
        if input_stream != self._input_stream:
            self._input_stream = input_stream


    # Method that interprets the code
    # If code and labels are provided, it updates the code and labels
    # If input_stream is provided, it updates the input_stream
    # If force_exit_after_interpret is True, it will force exit after interpreting
    # Errors are handled by decorator
    @e.ErrorHandler.handle_error
    def interpret(self, force_exit_after_interpret = False, code = None, labels = None, input_stream = None):
        # Set up the initial state of the program if called multiple times
        if code != None:
            if labels == None:
                self.error_message = "Labels must be provided if code is provided."
                return 99
            self.update_code(code, labels)
        if input_stream != None:
            self.update_input_stream(input_stream)
        # Reset interpreter before interpreting  
        self.reset(force_exit_after_interpret)

        # if there is no code, return 0
        if not self.code:
            return 0
        lenght = len(self.code)
        # Run the program
        while self._pc < lenght:
            # self.INSTRUCTIONS is a dictionary that maps instruction names to their methods
            #                                                               0       1      2     3
            # code is list of instructions  instruction is in format [instruction, arg1, arg2, arg3]
            # active instruction: self.code[self._pc][0]
            # argument 1: self.code[self._pc][1]
            # argument 2: self.code[self._pc][2]
            # argument 3: self.code[self._pc][3]
            # Run Method that implements the instruction by name
            err_code = self.INSTRUCTIONS[self.code[self._pc][0]](self)
            # If there was an error, return the error code or if the instruction was EXIT, return the exit code
            if err_code != 0 or self.code[self._pc][0] == "EXIT":
                return err_code
            # Increment the instruction count
            self._instruction_count += 1
            # Increment the program counter
            self._pc += 1
        # If the program ended normally, return 0
        return 0
