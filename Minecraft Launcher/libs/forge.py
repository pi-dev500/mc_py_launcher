import requests
import subprocess
from bs4 import BeautifulSoup
def get_compatible_versions():
    url="https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml"
    response=requests.get(url)
    if response.status_code == 200:
        # Analyse le contenu HTML de la page avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Recherche les balises <a> contenant les liens de téléchargement
        forges = soup.find_all('version')

        # Parcours des liens de téléchargement et récupération des noms de fichiers
        versions=dict()
        for forge in forges:
            mc_v=forge.text.split('-')[0]
            if not mc_v in versions.keys():
                versions[mc_v]=list()
            versions[mc_v].append(forge.text)
        return versions
        
    else:
        print('Erreur lors de la requête HTTP')
print(get_compatible_versions())