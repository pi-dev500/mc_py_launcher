import requests
import subprocess
import zipfile
import wget
import os
from bs4 import BeautifulSoup
def download_forge(version):
    temp_dir=os.path.expanduser("~/.minecraft/.TMP")
    if int(version.split(".")[1])>5:
        mode="universal.jar" # I think that it replace the base client, but I did not have the time to see that.
        url="https://maven.minecraftforge.net/net/minecraftforge/forge/"+version+"/"+version+"-universal.jar"
    elif version.split(".")[1] > 2 :
        mode="universal.zip" # I think that it works like client. zip mode, but not sure at all
        url="https://maven.minecraftforge.net/net/minecraftforge/forge/"+version+"/"+version+"-universal.zip"
    else:
        mode="client.zip" # must be unzipped in the base client jar
        url="https://maven.minecraftforge.net/net/minecraftforge/forge/"+version+"/"+version+"-client.zip"
    os.makedir(temp_dir)
    os.chdir(temp_dir)
    filename=wget.download(url)
    mc_version=version.split("-")[0]
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