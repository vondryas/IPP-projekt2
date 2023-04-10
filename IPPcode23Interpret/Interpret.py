from . import ArgumentParser
from . import XmlParser
from . import SemanticAnalyzer
from . import TacInterpret

class Interpret():

    def __init__(self):
        self.argument_parser = ArgumentParser.ArgumentParser()
        self.xml_parser = XmlParser.XmlParser()
        self.semantic_analysis = SemanticAnalyzer.SemanticAnalyzer()
        self.ippcode_interpret = TacInterpret.TACInterpret()

    def run_interpret(self, force_exit_after_interpret=True):
        self.argument_parser.parse_args()
        self.xml_parser.parse_to_interpreter(self.argument_parser.args.source_file)
        self.semantic_analysis.check_semantic(self.xml_parser.code)
        if self.argument_parser.args.input_file is None:
            return self.ippcode_interpret.interpret(force_exit_after_interpret, self.xml_parser.code, self.semantic_analysis.labels)
        else:
            with open(self.argument_parser.args.input_file, "r") as f:
                return self.ippcode_interpret.interpret(force_exit_after_interpret, self.xml_parser.code, self.semantic_analysis.labels, f)