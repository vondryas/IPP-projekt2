import sys


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


class nilType(type):

    def __repr__(cls):
        return cls.__name__


class nil(metaclass=nilType):

    def __new__(cls, name):
        obj = object.__new__(cls)
        return obj

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, nil)

    def __ne__(self, other):
        return not isinstance(other, nil)

    def __repr__(self):
        return ""


class InterpretData:

    _slots__ = ("_code", "_labels", "_pc",
                "_global_frame", "_local_frames",
                "_temporary_frame", "_call_stack",
                "_data_stack", "_instruction", "_arg1",
                "_arg2", "_arg3", "FRAMES", "TYPES",
                "error_message", "_instruction_count"
                "_input_stream")

    def __init__(self, code: list, labels: dict, input_stream=sys.stdin):
        self.code = code
        self._labels = labels
        self._pc = 0
        self._global_frame = {}
        self._local_frames = []
        self._temporary_frame = None
        self._call_stack = []
        self._data_stack = []
        self._instruction = ""
        self._arg1 = ""
        self._arg2 = ""
        self._arg3 = ""
        self._instruction_count = 0
        self.FRAMES = {"GF": self._global_frame,
                       "LF": self._local_frames, "TF": self._temporary_frame}
        self.TYPES = {"int": int, "string": str,
                      "bool": ExecuterUtils.to_bool, "nil": nil}
        self._input_stream = sys.stdin if input_stream is None else input_stream
        self.error_message = ""


class ExecuterUtils(InterpretData):

    __slots__ = ()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def instruction(func):
        setattr(func, "Instruction", True)
        return func

    # If method has instruction decorator

    @staticmethod
    def is_instruction(func):
        return hasattr(func, "Instruction")

    @staticmethod
    def to_bool(var: str):
        return True if var.upper() == "TRUE" else False

    @staticmethod
    def from_bool(var: bool):
        return "true" if var else "false"

    def parse_sym(self):
        frame, var_name = self._arg1.split("@", 1)
        return frame, var_name

    def parse_2sym(self):
        first, second = self._arg1.split("@", 1)
        third, fourth = self._arg2.split("@", 1)
        return first, second, third, fourth

    def parse_3sym(self):
        first, second = self._arg1.split("@", 1)
        third, fourth = self._arg2.split("@", 1)
        fifth, sixth = self._arg3.split("@", 1)
        return first, second, third, fourth, fifth, sixth

    def parse_lab_2sym(self):
        first, second = self._arg2.split("@", 1)
        third, fourth = self._arg3.split("@", 1)
        return first, second, third, fourth

    def top_frame(self, lst):
        if type(lst) == list:
            try:
                lst = lst[-1]
            except IndexError:
                raise NotExistingFrame(self, "")
        return lst

    # Frame = True, Sym = False
    @raise_again_err_decorator
    def get_sym_value(self, frame_or_sym, type_key, value_key, none_check=True):
        if frame_or_sym:
            try:
                # Frame
                value = ExecuterUtils.top_frame(
                    self, self.FRAMES[type_key])[value_key]
                if none_check and value is None:
                    raise MissingOperandValue(
                        self, f"Missing operand value in program counter: {self._pc}")
                return value
            except KeyError:
                raise NotExistingVariable(
                    self, f"No variable {value_key} in frame when calling instruction {self._instruction} in program counter: {self._pc}.")
        else:
            # Sym
            try:
                return self.TYPES[type_key](value_key)
            except ValueError:
                if type_key == "int":
                    try:
                        return self.TYPES[type_key](value_key, 16)
                    except ValueError:
                        return self.TYPES[type_key](value_key, 8)

    @raise_again_err_decorator
    def set_var_value(self, frame_type_key, value_key, value_to_set):
        try:
            ExecuterUtils.top_frame(self, self.FRAMES[frame_type_key])[
                value_key] = value_to_set
        except KeyError:
            raise NotExistingVariable(
                self, f"No variable {value_key} in frame when calling instruction {self._instruction} in program counter: {self._pc}.")

    @raise_again_err_decorator
    def calculation(self, operation, valid_types, mode=""):
        frame, var_name, frame_sym1, name_sym1, frame_sym2, name_sym2 = ExecuterUtils.parse_3sym(
            self)

        first_value = ExecuterUtils.get_sym_value(
            self, frame_sym1 in self.FRAMES, frame_sym1, name_sym1)
        second_value = ExecuterUtils.get_sym_value(
            self, frame_sym2 in self.FRAMES, frame_sym2, name_sym2)

        if "eq" == mode and (type(first_value) == nil or type(second_value) == nil):
            ExecuterUtils.set_var_value(
                self, frame, var_name, (first_value == second_value))
            return 0

        if "div" == mode and second_value == 0:
            BadOperandValue(
                self, f"Division by zero in program counter: {self._pc}")

        for _type in valid_types:
            if type(first_value) == _type and type(second_value) == _type:
                ExecuterUtils.set_var_value(self, frame, var_name,
                                            operation(first_value, second_value))
                return 0

        raise BadOperandTypes(
            self, f"Invalid operand types in program counter: {self._pc} on instruction {self._instruction}")


class Executer(ExecuterUtils, InterpretData):

    __slots__ = ()

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

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def create_frame(self):
        self._temporary_frame = {}
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def push_frame(self):
        if self._temporary_frame == None:
            raise NotExistingFrame(
                self, f"Missing frame in program counter: {self._pc} in instruction {self._instruction}")
        else:
            self._local_frames.append(self._temporary_frame)
            self._temporary_frame = None
            return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def pop_frame(self):
        # if _local_frames list is empty
        if not self._local_frames:
            raise NotExistingFrame(
                self, f"Missing frame in program counter: {self._pc} in instruction {self._instruction}")
        else:
            self._temporary_frame = self._local_frames.pop()
            return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def def_var(self):
        frame, var_name = self._arg1.split("@", 1)
        if var_name in Executer.top_frame(self, self.FRAMES[frame]):
            raise RedefiningVariable(self, f"Variable {frame}@{var_name} redefining on program counter {self._pc}.")
        Executer.set_var_value(self, frame, var_name, None)
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def call(self):
        self._call_stack.append(self._pc)
        self._pc = self._labels[self._arg1]
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _return(self):
        if not self._call_stack:
            MissingOperandValue(
                self, f"Missing return value in program counter: {self._pc}")
        else:
            self._pc = self._call_stack.pop()
            return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def pushs(self):
        frame, var_name = self._arg1.split("@", 1)
        # Push value to data stack
        self._data_stack.append(Executer.get_sym_value(
            self, frame in self.FRAMES, frame, var_name))
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def pops(self):
        frame, var_name = self._arg1.split("@", 1)
        if not self._data_stack:
            return 56
        else:
            Executer.set_var_value(self, frame, var_name,
                                   self._data_stack.pop())
            return 0

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
        return Executer.calculation(self, lambda x, y: x == y, [int, bool, str, nil], "eq")

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
        return Executer.calculation(self, lambda x, y: not x, [bool])

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def int2char(self):
        var_frame, var_name, sym_frame, sym_name = Executer.parse_2sym(self)
        value = Executer.get_sym_value(
            self, sym_frame in self.FRAMES, sym_frame, sym_name)
        try:
            value = chr(value)
        except ValueError:
            raise StringError(
                self, f"Invalid value for int2char: {value} on program counter {self._pc}.")
        except TypeError:
            raise BadOperandTypes(
                self, f"Invalid operand type for int2char: {type(value)} on program counter {self._pc}.")

        Executer.set_var_value(self, var_frame, var_name, value)
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def str2int(self):
        var_frame, var_name, sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_3sym(
            self)
        value = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        index = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        try:
            value = ord(value[index])
        except IndexError:
            raise StringError(
                self, f"Invalid index for str2int: {index} on program counter {self._pc}.")

        Executer.set_var_value(
            self, var_frame, var_name, value)
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def read(self):
        frame, var_name = Executer.parse_sym(self)
        try:
            value = self.TYPES[self._arg2](self._input_stream.readline().strip())
        except ValueError:
            value = nil(None)
        Executer.set_var_value(self, frame, var_name, value)
        return 0

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

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def concat(self):
        var_frame, var_name, sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_3sym(
            self)
        value1 = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        value2 = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        if type(value1) != str or type(value2) != str:
            raise BadOperandTypes(
                self, f"Invalid operand types for concat: {type(value1)} and {type(value2)} on program counter {self._pc}.")
        value = value1 + value2
        Executer.set_var_value(self, var_frame, var_name, value)
        return 0

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
        try:
            value = string[index]
        except IndexError:
            raise StringError(
                self, f"Invalid index for get_char: {index} on program counter {self._pc}.")
        Executer.set_var_value(self, var_frame, var_name, value)
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def set_char(self):
        var_frame, var_name, sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_3sym(
            self)
        string = Executer.get_sym_value(
            self, var_frame in self.FRAMES, var_frame, var_name)
        index = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        value = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        if type(string) != str or type(index) != int or type(value) != str:
            raise BadOperandTypes(
                self, f"Invalid operand type for set_char: {type(string)}, {type(index)} and {type(value)} on program counter {self._pc}.")
        try:
            string = string[:index] + value[0] + string[index + 1:]
        except IndexError:
            raise StringError(
                self, f"Invalid index for set_char: {index} on program counter {self._pc}.")
        Executer.set_var_value(self, var_frame, var_name, string)
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def _type(self):
        var_frame, var_name, sym_frame, sym_name = Executer.parse_2sym(self)
        value = Executer.get_sym_value(
            self, sym_frame in self.FRAMES, sym_frame, sym_name, False)
        if value is None:
            type_ = ""
        else:
            type_ = type(value).__name__
        Executer.set_var_value(self, var_frame, var_name, type_)
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def label(self):
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def jump(self):
        self._pc = self._labels[self._arg1]
        return 0

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def jump_if_eq(self):
        sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_lab_2sym(
            self)
        value1 = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        value2 = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        for type_ in [int, str, bool]:
            if (type(value1) == type_ and type(value2) == type_) or (type(value1) == nil or type(value2) == nil):
                if value1 == value2:
                    self._pc = self._labels[self._arg1]
                return 0
        raise BadOperandTypes(
            self, f"Invalid operand types for jump_if_eq: {type(value1)} and {type(value2)} on program counter {self._pc}.")

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def jump_if_n_eq(self):
        sym1_frame, sym1_name, sym2_frame, sym2_name = Executer.parse_lab_2sym(
            self)
        value1 = Executer.get_sym_value(
            self, sym1_frame in self.FRAMES, sym1_frame, sym1_name)
        value2 = Executer.get_sym_value(
            self, sym2_frame in self.FRAMES, sym2_frame, sym2_name)
        for type_ in [int, str, bool]:
            if (type(value1) == type_ and type(value2) == type_) or (type(value1) == nil or type(value2) == nil):
                if value1 != value2:
                    self._pc = self._labels[self._arg1]
                return 0
        raise BadOperandTypes(
            self, f"Invalid operand types for jump_if_n_eq: {type(value1)} and {type(value2)} on program counter {self._pc}.")

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

    @ExecuterUtils.instruction
    @ExecuterUtils.return_err_code_decorator
    def d_print(self):
        sym_frame, sym_name = Executer.parse_sym(self)
        value = Executer.get_sym_value(
            self, sym_frame in self.FRAMES, sym_frame, sym_name)
        print(value, file=sys.stderr)
        return 0

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
        print("top of stack is at the bottom of the list)", file=sys.stderr)
        print(f"local frames: {self._local_frames}", file=sys.stderr)
        print(f"call stack: {self._call_stack}", file=sys.stderr)
        print(f"data stack: {self._data_stack}", file=sys.stderr)
        return 0

    INSTRUCTIONS = {method_name.replace("_", "").upper(): method
                    for (method_name, method) in locals().items()
                    if ExecuterUtils.is_instruction(method)}


class TACInterpreter(Executer, InterpretData):

    __slots__ = ()

    def __init__(self, code, labels, input_stream = sys.stdin):
        InterpretData.__init__(self, code, labels, input_stream)

    def interpret(self):
        self.__init__(self.code, self._labels, self._input_stream)
        if not self.code:
            return 0
        while self._pc < len(self.code):
            instruction_len = len(self.code[self._pc])
            self._arg1 = self.code[self._pc][1] if instruction_len > 1 else None
            self._arg2 = self.code[self._pc][2] if instruction_len > 2 else None
            self._arg3 = self.code[self._pc][3] if instruction_len > 3 else None
            self._instruction = self.code[self._pc][0]
            err_code = self.INSTRUCTIONS[self._instruction](self)
            if err_code != 0 or self._instruction == "EXIT":
                return err_code
            self._instruction_count += 1
            self._pc += 1
        return 0
