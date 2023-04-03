import argparse
import sys
import io

class MyArgumentParser(argparse.ArgumentParser):

    # Overriding the method to write custom error when combining -h/--help with other arguments
    def _parse_known_args(self, arg_strings, *args, **kwargs):
        # Check if '-h' or '--help' is present with other arguments
        if ('-h' in arg_strings or '--help' in arg_strings) and len(arg_strings) > 1:
            self.error("'-h'/'--help' cannot be used with other arguments.")
        return super()._parse_known_args(arg_strings, *args, **kwargs)

    # Overriding to return error code 10 instead of 2
    def error(self, message):
        self.print_usage(sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(10, ('%(prog)s: error: %(message)s\n') % args)

class ArgumentParser:

    __slots__ = ("args", "parser", "input", "error_message")

    def __init__(self):
        self.parser = MyArgumentParser(
            description="Interpreter of IPPcode23 interpreting xml IPPcode23")
        self.parser.add_argument(
            "-s", "--source", dest="source_file", help="source file")
        self.parser.add_argument(
            "-i", "--input", dest="input_file", help="input file")
        self.args = None
        self.input = ""
        self.error_message = ""

    def parse_args(self):
        self.args = self.parser.parse_args()

        if self.args.source_file is None and self.args.input_file is None:
            self.error_message = "No mandatory arguments found at least one of them is required"
            return 10

        if self.args.input_file is not None:
            try:
                with open(self.args.input_file, "r") as file:
                    self.input = file.read()
                self.input = io.StringIO(self.input)
            except FileNotFoundError:
                self.error_message = f"Input file {self.args.input_file} not found"
                return 11
            except PermissionError:
                self.error_message = f"Input file {self.args.input_file} is not readable. No permission"
                return 11
        if self.args.source_file is not None:
            try:
                with open(self.args.source_file, "r") as file:
                    pass
            except FileNotFoundError:
                self.error_message = f"Source file {self.args.source_file} not found"
                return 11
            except PermissionError:
                self.error_message = f"Source file {self.args.source_file} is not readable. No permission"
                return 11
        return 0