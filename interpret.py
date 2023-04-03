import IPPcode23Interpret.TacInterpret as inter
import IPPcode23Interpret.SemanticAnalyzer as s
import IPPcode23Interpret.XmlParser as xml
import IPPcode23Interpret.ErrorHandler as e
import IPPcode23Interpret.ArgumentParser as a


if __name__ == "__main__":
    err = e.ErrorHandler()
    arg = a.ArgumentParser()
    err.handle(arg.parse_args(), arg.error_message)
    rq = xml.XmlParser()
    err.handle(rq.parse_to_interpreter(arg.args.source_file), rq.error_message)
    sem = s.SemanticAnalyzer()
    err.handle(sem.check_semantic(rq.code), sem.error_message)
    aha = inter.TACInterpreter(rq.code, sem.labels, arg.input)
    err.handle(aha.interpret(), aha.error_message, True)