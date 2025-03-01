import yaml
import os


def read_config(file_path):
    """
    Lit un fichier de configuration YAML et retourne la valeur du champ 'status'.

    :param file_path: Chemin vers le fichier de configuration.
    :type file_path: str
    :return: Valeur du champ 'status' ou None en cas d'erreur ou d'absence du fichier.
    :rtype: str ou None
    """
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as file:
        try:
            config = yaml.safe_load(file)
            return config.get("status", "")
        except yaml.YAMLError as e:
            print(f"Erreur de lecture du fichier YAML : {e}")
            return None

def spilt_uuid (v, separator:str = '-'):
    lst = v.split(separator)
    uuid = lst[0]
    v = separator.join(lst[1:])
    return  uuid, v