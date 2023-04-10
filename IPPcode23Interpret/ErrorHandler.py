import sys

# Class that has static decorator that will handle errors
class ErrorHandler:
    
    # Decorator that will handle errors
    # If function has no arguments it will return output of decorated function
    # If function has arguments it will check if it is instance of class that has error_message attribute
    # If it has it will check if error_code is in range 0 - 49
    # If it is it will check if error_message is empty
    # If it is it will return 0 if not forced exit
    # If it has forced exit it will exit with error code
    @staticmethod
    def handle_error(func):
        def wrapper(*args, **kwargs):
            # Execute decorated function
            error_code = func(*args, **kwargs)
            # Classes in this package will always have attribute error_message and error_code always be int
            # xml and argument parser and interpret EXIT error codes are in range 0 - 49
            # All classes in will have force_exit attribute
            if error_code > -1 and error_code < 50:
                # if no error message and not forced exit it will return 0 else it will exit with error code
                if not args[0].error_message:
                    if args[0].force_exit:
                        exit(error_code)
                    else:
                        return 0
                # xml or argument parser error codes
                else:
                    print(args[0].error_message, file=sys.stderr)
                    exit(error_code)
            # other error codes
            else:
                print(args[0].error_message, file=sys.stderr)
                exit(error_code)
        return wrapper
    
class ErrorHandable(ErrorHandler):

    def __init__(self, force_exit=False):
        self.error_message = ""
        self.force_exit = force_exit
