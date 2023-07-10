import requests
from bs4 import BeautifulSoup
import subprocess

def get_and_install(file):
    url='http://optifine.net/download?f='+file
    subprocess.run(['wget','-q','--show-progress','--progress=bar:force',url,'-O',file])
    subprocess.run(['java','-cp',file,'optifine.Installer'])
    subprocess.run(['rm','-f',file])
    print(file[:-4],'installed')

def get_versions_list():
    url = 'https://optifine.net/downloads'
    response = requests.get(url)
    # Vérifie si la requête a réussi
    if response.status_code == 200:
        # Analyse le contenu HTML de la page avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Recherche les balises <a> contenant les liens de téléchargement
        download_links = soup.find_all('a', {'href': True}, text=lambda text: text and '(mirror)' in text.lower())

        # Parcours des liens de téléchargement et récupération des noms de fichiers
        versions=list()
        for link in download_links:
            filename = link['href'].split('/')[-1]
            #print(str(link).split('"')[1].split('=')[1])
            versions.append(str(link).split('"')[1].split('=')[1])
        #get(versions[0])
        return versions
        
    else:
        print('Erreur lors de la requête HTTP')

def get_compatible_versions():
    versions_compat=dict()
    for of_version in get_versions_list():
        mc_version = of_version.replace("preview_OptiFine","OptiFine").split('_')[1]
        if not mc_version in versions_compat.keys():
            versions_compat[mc_version]=list()
        versions_compat[mc_version].append(of_version)
    return  versions_compat

print(get_compatible_versions())