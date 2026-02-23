import yaml

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

def get_config():
    return config