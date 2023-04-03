import sys


class ErrorHandler:

    def handle(self, error_code, error_message="", exite=False):
        if error_code > -1 and error_code < 50:
            if not error_message:
                if exite:
                    exit(error_code)
            else:
                print(error_message, file=sys.stderr)
                exit(error_code)
        else:
            print(error_message, file=sys.stderr)
            exit(error_code)
