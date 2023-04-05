import IPPcode23Interpret.TacInterpret as inter
import IPPcode23Interpret.SemanticAnalyzer as s
import IPPcode23Interpret.XmlParser as xml
import IPPcode23Interpret.ArgumentParser as a
import sys


if __name__ == "__main__":
    argument_parser = a.ArgumentParser()
    
    argument_parser.parse_args()
    
    xml_parser = xml.XmlParser()
    
    xml_parser.parse_to_interpreter(xml_file = argument_parser.args.source_file)
    
    semantic_analysis = s.SemanticAnalyzer()

    semantic_analysis.check_semantic(code = xml_parser.code)

    if argument_parser.args.input_file is None:
        ippcode_interpreter = inter.TACInterpreter(
            code = xml_parser.code, labels = semantic_analysis.labels)

        ippcode_interpreter.interpret(force_exit_after_interpret=True)
        
    else:
        with open(argument_parser.args.input_file, "r") as f:
            
            ippcode_interpreter = inter.TACInterpreter(
                code = xml_parser.code, labels = semantic_analysis.labels, input_stream = f)

            ippcode_interpreter.interpret(force_exit_after_interpret=True)