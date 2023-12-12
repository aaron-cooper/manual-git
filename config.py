import re
import sys

class Config:
    def __init__(self):
        self.sections={}

    @staticmethod
    def from_file(path: str):
        section_re = re.compile(r'^\s*\[\s*(?P<section>[a-zA-Z0-9\-\.]+)\s*("(?P<subsection>[a-zA-Z0-9\-\.]+)")?\s*\]\s*$')
        assignment_re = re.compile(r"^\s*(?P<name>[a-zA-Z][a-zA-Z0-9\-]*)\s*=\s*(?P<value>\S|\S.*\S)\s*$")
        empty_line_re = re.compile(r"^\s*$")
        curr_section = None
        config = Config()
        with open(path, "r") as f:
            while (line := f.readline()) != "":
                if result := section_re.search(line):
                    curr_section = result.group('section').lower()
                    if subsection := result.group('subsection'):
                        curr_section += f'+{subsection}'
                elif result := assignment_re.search(line):
                    if not curr_section:
                        raise SyntaxError("Invalid config file: assignment appears before any section.")
                    config.set_config(curr_section, result.group('name').lower(), result.group('value'))
                elif empty_line_re.fullmatch(line):
                    "do nothing"
                else:
                    raise SyntaxError("Invalid config file, could not parse line: " + line)
        return config

    def set_config(self, section, name, value):
        self.verify_config(section, name, value)
        section = section.lower()
        name = name.lower()
        if section not in self.sections:
            self.sections[section] = {}
        self.sections[section][name] = value

    def verify_config(self, section, name, value):
        section_pattern = r"^[a-zA-Z\-\.]+(\+[a-zA-Z\-\.]+)?$"
        if not re.match(section_pattern, section):
            raise ValueError("section", f"Section must match the pattern: \\{section_pattern}\\")
        name_pattern = r"^[a-zA-Z\.]+$"
        if not re.match(name_pattern, name):
            raise ValueError("name", f"Name must match the pattern: \\{name_pattern}\\")
        if not re.match(r"^(\S|\S.*\S)+$", value):
            raise ValueError("value", f"Value may not begin or end with white space.")



    def drop_config(self, section, name):
        section = section.lower()
        name = name.lower()
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
                if '+' in section:
                    splits = section.split('+')
                    print(f"[{splits[0]} \"{splits[1]}\"]", file=f)
                else:
                    print(f"[{section}]", file=f)
                for name in self.sections[section]:
                    print(f"\t{name} = {self.sections[section][name]}", file=f)


def main(args):
    config_file_path = args.root + '/.git/config'
    config = Config.from_file(config_file_path)
    try:
        config.set_config(args.section, args.variable, args.value)
        config.save_to_file(config_file_path)
    except ValueError as e:
        print(e.args[1], file=sys.stderr)
        exit(1)