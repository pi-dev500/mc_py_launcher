import requests
from bs4 import BeautifulSoup
import subprocess

def get_and_install(file):
    url='http://optifine.net/download?f='+file
    subprocess.run(['wget','-q','--show-progress','--progress=bar:force',url,'-O',file])
    subprocess.run(['java','-cp',file,'optifine.Installer'])
    subprocess.run(['rm','-f',file])
    print(file,'installed')
def get_version_list():
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
            print(str(link).split('"')[1].split('=')[1])
            versions.append(str(link).split('"')[1].split('=')[1])
        #get(versions[0])
        return versions
        
    else:
        print('Erreur lors de la requête HTTP')

