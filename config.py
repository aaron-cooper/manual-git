import re

class Config:
    def __init__(self):
        self.sections={}

    @staticmethod
    def from_file(path: str):
        section_re = re.compile(r"^\s*\[(?P<section>[a-zA-Z0-9\-\.]+)\]\s*$")
        assignment_re = re.compile(r"^\s*(?P<name>[a-zA-Z][a-zA-Z0-9\-]*)\s*=\s*(?P<value>\S+)\s*$")
        empty_line_re = re.compile(r"^\s*$")
        curr_section = None
        config = Config()
        with open(path, "r") as f:
            while (line := f.readline()) != "":
                if result := section_re.search(line):
                    curr_section = result.group('section').lower()
                elif result := assignment_re.search(line):
                    if not curr_section:
                        raise SyntaxError("Invalid config file: assignment appears before any section.")
                    config.set_config(curr_section, result.group('name'), result.group('value'))
                elif empty_line_re.fullmatch(line):
                    "do nothing"
                else:
                    raise SyntaxError("Invalid config file, could not parse line: " + line)
        return config

    def set_config(self, section, name, value):
        if section not in self.sections:
            self.sections[section] = {}
        self.sections[section][name] = value

    def drop_config(self, section, name):
        if section not in self.sections:
            return
        if name not in self.sections[section]:
            return
        self.sections[section].pop(name)
        if len(self.sections[section]) == 0:
            self.sections.pop(section)

    def save_to_file(self, path: str):
        with open(path, "w") as f:
            for section in self.sections:
                print(f"[{section}]", file=f)
                for name in self.sections[section]:
                    print(f"\t{name} = {self.sections[section][name]}", file=f)