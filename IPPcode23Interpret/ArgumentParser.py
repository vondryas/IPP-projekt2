import argparse
import sys
import os
from . import ErrorHandler as e

# Modified argparse library
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

# Class for parsing arguments
# Using modified argparse library
class ArgumentParser(e.ErrorHandable):

    __slots__ = ("args", "parser", "error_message", "force_exit")

    def __init__(self, force_exit=False):
        self.parser = MyArgumentParser(
            description="Interpreter of IPPcode23 interpreting xml IPPcode23")
        
        self.parser.add_argument(
            "-s", "--source", dest="source_file", help="source file")
        
        self.parser.add_argument(
            "-i", "--input", dest="input_file", help="input file")
        super().__init__(force_exit)

    def _reset(self, force_exit=False):
        self.args = None
        super().__init__(force_exit)

    # Parse arguments and return error code 0 if everything is ok
    # Return error code 10 if no mandatory arguments are found or combining -h/--help with other arguments
    # Return error code 11 if input file or source file is not found or is not readable
    # Errors are handled by decorator
    @e.ErrorHandable.handle_error
    def parse_args(self, force_exit=False):
        # Reset
        self._reset(force_exit)

        self.args = self.parser.parse_args()

        if self.args.source_file is None and self.args.input_file is None:
            self.error_message = "No mandatory arguments found at least one of them is required (-s/--source or -i/--input)"
            return 10

        if self.args.input_file is not None:
            if not os.path.exists(self.args.input_file):
                self.error_message = f"Input file {self.args.input_file} not found"
                return 11
            elif not os.access(self.args.input_file, os.R_OK):
                self.error_message = f"Input file {self.args.input_file} is not readable. No permission"
                return 11
            
        if self.args.source_file is not None:
            if not os.path.exists(self.args.source_file):
                self.error_message = f"Source file {self.args.source_file} not found"
                return 11
            elif not os.access(self.args.source_file, os.R_OK):
                self.error_message = f"Source file {self.args.source_file} is not readable. No permission"
                return 11
            
        return 0