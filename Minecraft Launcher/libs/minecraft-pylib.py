import json
import subprocess
import os
import optifine
#import wget # this library is a bit broken sometimes...
def wget(url,dest=None,opts=[]):
    if dest==None:
        dest=os.path.basename(url)
    return subprocess.check_output(["wget","-q",url,"-O",dest]+opts) # why not ?
def mv(file,newdest):
    return subprocess.run(['mv',file,newdest])
#Infos
cracked=True #Sorry, Mojang...
auth_player_name='Steve'
game_directory=os.path.expanduser("~/.minecraft")

launcher_name='java-minecraft-launcher' # Ha except it's a Python launcher...
launcher_version='0.1.0-b' # Currently in testing phase

auth_uuid='00000000-0000-0000-0000-000000000000' # in the final launcher, it will be chosen by the user if the game is cracked
auth_access_token='null'
user_type='legacy'
is_demo=False
custom_resolution=False
assets_root="${game_directory}/assets"
libraries_root="${game_directory}/libraries"
versions_root="${game_directory}/versions"
#Start configurating env...
env={}
env['auth_player_name']='Steve'
env['game_directory']=os.path.expanduser("~/.minecraft")

env['launcher_name']='java-minecraft-launcher' # Ha except it's a Python launcher...
env['launcher_version']='0.1.0-b'

env['auth_uuid']='00000000-0000-0000-0000-000000000000' # in the final launcher, it will be chosen by the user
env['auth_access_token']='null'
env['user_type']='legacy'
#env['is_demo']=False
#env['custom_resolution']=False
env['assets_root']="${game_directory}/assets"
env['libraries_root']="${game_directory}/libraries"
env['versions_root']="${game_directory}/versions"

cpu_bits=subprocess.check_output("getconf LONG_BIT",shell=True) # On the raspberry pi and other arms boards, that can be different of uname values
arch=subprocess.check_output("uname -m",shell=True)
if arch=="aarch64" and cpu_bits=="32":
    arch="armhf"
elif arch=="i686" or arch=="i386":
    arch="x86"
elif arch=="amd64":
    arch="x86"
#Minecraft
manifest_url="https://raw.githubusercontent.com/theofficialgman/piston-meta-arm32/main/mc/game/version_manifest_v2.json" # for arm32 only
if arch=="armv8l" or arch=="arm64" or arch=="aarch64":
    manifest_url="https://raw.githubusercontent.com/theofficialgman/piston-meta-arm64/main/mc/game/version_manifest_v2.json" # version for arm64
elif arch=="x86":
    manifest_url="https://launchermeta.mojang.com/mc/game/version_manifest.json" # legacy version (x86)
try:
    list_versions=json.loads(subprocess.check_output(["wget","-qO-",manifest_url]))
except:
    list_versions=json.loads(subprocess.check_output(["cat",os.path.expanduser("~/.minecraft/version_manifest.json")]))
versions={}
for i in list_versions["versions"]:
    versions[i["id"]]={"type": i["type"], "url": i["url"]}
#print(versions)
def get_download_list(mc_version):
    try:
        version_infos=json.loads(subprocess.check_output("wget -qO- " + versions[mc_version]["url"],shell=True))
        with open(os.path.join(game_directory,"versions",mc_version,mc_version+".json"),"w") as v_m:
            v_m.write(json.dumps(version_infos))
        os.system("mkdir -p ~/.minecraft/versions/" + mc_version + " && cd ~/.minecraft/versions/" + mc_version + " && wget -q " + versions[mc_version]["url"]  + " -O " + versions[mc_version]["url"].split("/")[-1])
        assets_list=json.loads(subprocess.check_output("wget -qO- " + version_infos["assetIndex"]["url"],shell=True))
        os.system("mkdir -p $HOME/.minecraft/assets/indexes && wget -q " + version_infos["assetIndex"]["url"] + " -O " + "~/.minecraft/assets/indexes/"+version_infos["assetIndex"]["url"].split("/")[-1])
    except:
        with open(os.path.join(game_directory,"versions",mc_version,mc_version+".json"),"r") as v_m:
            version_infos=json.loads(v_m.readlines()[0])
        with open(os.path.join(game_directory,"assets/indexes",version_infos['assets']+".json"),"r") as a_l:
            assets_list=json.loads(a_l.readlines()[0])
    #print(version_infos['arguments'])
    libraries=version_infos["libraries"]
    #print(version_infos)
    #print(assets_list)
    downloads_list=[]
    downloads_list.append([version_infos["downloads"]["client"]["url"], os.path.expanduser(os.path.join("~/.minecraft/versions/",mc_version,mc_version + ".jar")), version_infos["downloads"]["client"]["size"]])
    #print(version_infos["downloads"]["client"]["url"], os.path.expanduser(os.path.join("~/.minecraft",mc_version + ".jar")), version_infos["downloads"]["client"]["size"])
    total_download_size=version_infos["downloads"]["client"]["size"]
    def getasseturi(asset):
        return("https://resources.download.minecraft.net/" + asset["hash"][:2] + "/" + asset["hash"])
    def returnlibinfos(lib):
        if "classifiers" in lib["downloads"]:
            return(lib["downloads"]["classifiers"]["natives-linux"])
        else:
            return(lib["downloads"]["artifact"])

    for i in assets_list["objects"].keys():
        total_download_size=total_download_size+assets_list["objects"][i]["size"]
        downloads_list.append([getasseturi(assets_list["objects"][i]), os.path.expanduser(os.path.join("~/.minecraft/assets/objects",assets_list["objects"][i]["hash"][:2],assets_list["objects"][i]["hash"])), assets_list["objects"][i]["size"]])
        #print(getasseturi(assets_list["objects"][i]), os.path.expanduser(os.path.join("~/.minecraft/assets/objects",i)), assets_list["objects"][i]["size"])
    for i in libraries:
        total_download_size=total_download_size+returnlibinfos(i)["size"]
        downloads_list.append([returnlibinfos(i)["url"], os.path.expanduser(os.path.join("~/.minecraft/libraries",returnlibinfos(i)["path"])), returnlibinfos(i)["size"]])
        #print(returnlibinfos(i)["url"], os.path.expanduser(os.path.join("~/.minecraft/libraries",returnlibinfos(i)["path"])), returnlibinfos(i)["size"])
    print(downloads_list)
    #print("Total size:", round(total_download_size/(1024**2)), "Mo")
    return(downloads_list,total_download_size,version_infos)

def download_mc(assets,size,downloaded=0):
    percent=0
    print("(",percent,"percent ) ",end='')
    for asset in assets:
        #print(asset[1] + "... ",end='')
        os.makedirs(os.path.dirname(asset[1]),exist_ok=True)
        os.chdir(os.path.dirname(asset[1]))
        try:
            wget(asset[0],os.path.basename(asset[1]))
        except:
            print("problem while downloading",asset[1],"a retry is comming...")
            wget(asset[0],os.path.basename(asset[1]),opts=["--continue"])
        with open(os.path.join(game_directory,'downloaded.json'),'a') as alrd_file:
            alrd_file.write(str(asset)+'\n')
        downloaded+=asset[2]
        percent=int(downloaded*100/size)
        print("Done")
        print("(",percent,"percent ) ",end='')
    mv(os.path.join(game_directory,'downloaded.json'),os.path.join(game_directory,"versions",version))
    return 0
def extract_natives(version):
    #is it kcraft?
    with open(os.path.join(game_directory,"versions",version,version+".json"),"r") as v_m:
        version_manifest=json.loads(v_m.readlines()[0])
    natives=[]
    for lib in version_manifest['libraries']:
        if "classifiers" in lib['downloads']:
            if "natives-linux" in lib['downloads']['classifiers']:
                natives.append(os.path.expanduser(os.path.join("~/.minecraft/libraries/",lib['downloads']['classifiers']['natives-linux']['path'])))
    os.makedirs(os.path.expanduser(os.path.join("~/.minecraft/versions/",version,"natives")),exist_ok=True)
    os.chdir(os.path.expanduser(os.path.join("~/.minecraft/versions/",version,"natives")))
    for native in natives:
        os.system("unzip -uo '" + native+"'")
def create_launch_script(version):
    #parse the json to find how to launch minecraft
    final_arguments=["env", "MESA_GL_VERSION_OVERRIDE=3.3","/usr/lib/jvm/temurin-17-jdk-armhf/bin/java"]
    with open(os.path.join(game_directory,"versions",version,version+".json"),"r") as v_m:
        version_manifest=json.loads(v_m.readlines()[0])
    args_code=version_manifest['arguments']
    for arg in args_code['jvm']:
        if isinstance(arg, dict):
            for rule in arg['rules']:
                if rule['action'] == "allow":
                    allowed=False
                    for req in rule['os'].keys():
                        if req=="name" and rule['os'][req]=="linux":
                            allowed=True
                        elif req=="arch" and rule['os'][req]==arch:
                            allowed=True
                    if allowed==True:
                        if isinstance(arg['value'], list):
                            for argument in arg['value']:
                                final_arguments.append(argument)
                        else:
                            final_arguments.append(arg['value'])
        else:
            final_arguments.append(arg)
            if arg=="${classpath}":
                final_arguments.append("${main_class}")
    for arg in args_code['game']:
        if isinstance(arg, dict):
            for rule in arg['rules']:
                if rule['action'] == "allow":
                    allowed=False
                    for feature in rule['features'].keys():
                        if feature=="is_demo_user" and rule['features'][feature]==is_demo:
                            allowed=True
                        elif feature=="has_custom_resolution" and rule['features'][feature]==custom_resolution:
                            allowed=True
                        elif feature=="has_quick_plays_support" and rule['features'][feature]==False:
                            allowed=True
                        elif feature=="is_quick_play_singleplayer" and rule['features'][feature]==False:
                            allowed=True
                        elif feature=="is_quick_play_multiplayer" and rule['features'][feature]==False:
                            allowed=True
                        elif feature=="is_quick_play_realms" and rule['features'][feature]==False:
                            allowed=True
                    if allowed==True:
                        final_arguments.append(arg['value'])
        else:
            if not ((arg=='--xuid' or arg=='${auth_xuid}' or arg=="--clientId" or arg=="${clientid}") and cracked==True):
                final_arguments.append(arg)
            
    return final_arguments
def get_classpath(version):
    with open(os.path.join(game_directory,"versions",version,version+".json"),"r") as v_m:
        version_manifest=json.loads(v_m.readlines()[0])
    libs=version_manifest['libraries']
    libs_names=list()
    for lib in libs:
        if not lib['name'] in libs_names:
            libs_names.append(lib['name'])
    final=""
    #print(libs_names)
    for libname in libs_names:
        split=libname.split(':')
        group=split[0].replace('.','/')
        artifact=split[1]
        lib_version=split[2]
        list_files=os.listdir(os.path.join(os.path.expanduser("~/.minecraft/libraries"),group,artifact,lib_version))
        list_files=[os.path.join(os.path.expanduser("~/.minecraft/libraries"),group,artifact,lib_version,file) for file in list_files]
        final+=":".join(list_files)+":"
    final+=os.path.join(os.path.expanduser("~/.minecraft/versions"),version,version+".jar")
    return final
def launch(version):
    with open(os.path.join(game_directory,"versions",version,version+".json"),"r") as v_m:
        version_manifest=json.loads(v_m.readlines()[0])
    env['main_class']=version_manifest['mainClass']
    classpath=get_classpath(version)
    env['classpath']=classpath
    env['natives_directory']=os.path.expanduser(os.path.join("~/.minecraft/versions",version,"natives"))
    env['version_type']=version_manifest['type']
    env['version_name']=version
    env['assets_index_name']=version_manifest['assets']
    #print(env)
    text_sh=["#!/bin/bash\n","echo -ne '\e]0;Minecraft "+version+" Log\a'\n"]
    for var in env.keys():
        text_sh.append(var+"=\""+env[var]+"\"\n")
    
    text_sh.append("")
    for arg in create_launch_script(version):
        text_sh[-1]+='"'+arg+'" \\\n'
    with open(os.path.expanduser(os.path.join("~/.minecraft/versions",version,"launch.sh")),'w') as script:
        script.writelines(text_sh)
    os.chdir(os.path.expanduser("~/.minecraft"))
    subprocess.run(['chmod','+x',os.path.join(os.path.expanduser("~/.minecraft/versions",version,"launch.sh"))])
    return subprocess.Popen(["x-terminal-emulator","-e",os.path.expanduser(os.path.join("~/.minecraft/versions",version,"launch.sh")),"--title=Minecraft " + version + " Log"])
list_assets=get_download_list("1.20.1")
download_mc(list_assets[0],list_assets[1])
#extract_natives('1.20.1')
#launch("1.20.1")