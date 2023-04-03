class SemanticAnalyzer:

    __slots__ = ("labels", "error_message", "_expected_labels")

    def __init__(self):
        self.labels = {}
        self._expected_labels = []
        self.error_message = ""

    def add_label(self, label, pc):
        if label in self.labels:
            self.error_message = f"Label {label} on index {pc} is already defined in line {self.labels[label]}. Indexed from 0"
            return 52
        if label in self._expected_labels:
            self._expected_labels.remove(label)

        self.labels[label] = pc
        return 0

    def add_expected_label(self, label):
        if label not in self._expected_labels and label not in self.labels:
            self._expected_labels.append(label)

    def check_semantic(self, code):
        self.labels = {}
        self._expected_labels = []
        for instruction in code:
            if instruction[0] == "LABEL":
                if self.add_label(instruction[1], code.index(instruction)) != 0:
                    return 52
            elif instruction[0] in ["JUMP", "JUMPIFEQ", "JUMPIFNEQ", "CALL"]:
                self.add_expected_label(instruction[1])

        if self._expected_labels:
            self.error_message = f"Labels {self._expected_labels} are not defined"
            return 52

        return 0
