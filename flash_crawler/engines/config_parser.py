import yaml

class ConfigParserError(Exception):
    pass

class ConfigParser:
    def __init__(self, config_path) -> None:
        self.config = self.parse_config(config_path)
        self.check_config_structure(self.config)

    @staticmethod
    def parse_config(config_path):
        with open(config_path, "r") as stream:
            return yaml.safe_load(stream)
    
    @staticmethod
    def check_config_structure(config):
        if "page_type" not in config.keys():
            raise ConfigParserError("Wrong config file structure")
    
    def get_single_page_scenario(self, page_type):
        if page_type in list(self.config["page_type"].keys()):
            return self.config["page_type"][page_type]
        else:
            raise ConfigParserError("Provided page type not in config file")

    def get_containers_selector(self, page_type):
        page_scenario = self.get_single_page_scenario(page_type)
        if "containers" in page_scenario.keys():
            return page_scenario["containers"]["selector"]
        else:
            return None

    def get_containers_elements_selectors(self, page_type):
        page_scenario = self.get_single_page_scenario(page_type)
        return page_scenario["containers"]["elements"]

    def get_elements_selectors(self, page_type):
        page_scenario = self.get_single_page_scenario(page_type)
        if "elements" in page_scenario.keys():
            return page_scenario["elements"]
        else:
            return None
