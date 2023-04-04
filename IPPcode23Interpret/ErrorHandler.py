import sys

# Class for handling errors
class ErrorHandler:

    # Method that take error code and error message and print it to stderr
    # it exit program with error code or go on if ok
    # it can force exit program with error code
    def handle(self, error_code, error_message="", exite=False):
        # xml and argument parser and interpret EXIT error codes are in range 0 - 49 
        if error_code > -1 and error_code < 50:
            # if no error message it will continue if not forced exit
            if not error_message:
                if exite:
                    exit(error_code)
            # xml or argument parser error codes
            else:
                print(error_message, file=sys.stderr)
                exit(error_code)
        # other error codes
        else:
            print(error_message, file=sys.stderr)
            exit(error_code)
