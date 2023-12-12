from config import Config

def add_remote(root_path: str, name: str, url: str):
    config_path = root_path + '/.git/config'
    config = Config.from_file(config_path)
    config.set_config(f"remote+{name}", "url", url)
    config.save_to_file(config_path)

def main(ops):
    root_path = ops.root
    match ops.remote_command:
        case "add":
            add_remote(root_path, ops.name, ops.url)