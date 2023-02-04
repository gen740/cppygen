import yaml


with open("./cppygen_config.yml", "r") as f:
    data = yaml.safe_load(f)


print(data)
