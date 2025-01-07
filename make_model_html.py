# make_model_html.py
# this program reads the sage_cache.json, pulls more data from civitai, then writes out models that hava a lastused timestamp to a sqlite3 database in memory
# it writes out models that do not have a last used timestamp to internal dictionaries. It then uses these data sources to create 2 html files.
# loras.html contains all comfyui loras starting with the most recently used
# xpoints.html contains all comfyUI checkpoints starting with the most recently used
# The format and composition of the html tables can be customized as follows
# You can customize the output table format completely.
# You can add fields, remove fields, change the column order, whatever you like    
# Number indicates which column in table, zero means do not include this field
# If you need 10 or more columns use hex (A = 10, B = 11, etc)       
# A 14 character formatted string can be passed as a shell parameter:
#
#       7-1002300045670-Embed images 0=False, 1=True
#       | |||||||||||└- Last used date 
#		| ||||||||||└-- Prompt
#		| |||||||||└--- Example image
#		| ||||||||└---- Denoise info
#		| |||||||└----- Steps used
#		| ||||||└------ Model civitai ID
#		| |||||└------- Model hash
#		| ||||└-------- Civitai URL
#		| |||└--------- Trigger words
#		| ||└---------- Model type (LORA or Checkpoint)
#		| |└----------- Base model (Flux, Pony, etc)
#		| └------------ Model name
#		└-------------- Number of columns
#
# The example and default string tells the program to create a 7 column table containing
# Model name in column 1
# Trigger words in column 2
# Civitai URL in column 3
# Denoise info in column 4
# Example image in column 5
# Prompt in column 6
# Last used date in column 7

import pathlib
import hashlib
import requests
import json
import folder_paths
#import comfy.utils
import time
import sqlite3
import datetime
import sys
import html

import urllib.request 

from pathlib import Path

def parse_json_file(filename):
    try:
        # Opening and reading from a JSON filename, which is expected to be valid UTF-8 encoded text file.
        
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)  # Parse the contents of the .json file into Python dictionary/object structure.
            
            return data
    except FileNotFoundError:
        print("The specified JSON filename was not found.")
    except IOError:
        print("An I/O error occurred while reading from or opening the json_filename")
    except Exception as e:
        # Catching all other exceptions such as malformed data in your .json file.
        
        print(f"Exception caught when parsing JSON File, Error message is {e}")

def get_civitai_json(hash):
    try:
        r = requests.get("https://civitai.com/api/v1/model-versions/by-hash/" + hash)
        r.raise_for_status()
    except Exception as err:
        print(f"Other error occurred: {err}")
        return {}
    else:
 #       print("Success!")
        return r.json()
#    except HTTPError as http_err:
#        print(f"HTTP error occurred: {http_err}")
#        return {"error": "HTTP error occurred: " + http_err}
    return r.json()
    
def download_image(url, save_as):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_as, 'wb') as f:
            f.write(response.content)
    else:
        print("Failed to download image!")

def getFNfromURL(url):

  parts = url.split('/')

  return parts[len(parts) - 1]

    
def pull_json(self, hash):
    the_json = {}
    try:
        the_json = get_civitai_json(hash)
    except:
        the_json = {}
    return(f"{json.dumps(the_json)}",)
    
def x2int(hexdig):
    if hexdig.isdigit():
        return(int(hexdig))
        
    match hexdig:
        case "A":
            return(10)
        case "B":
            return(11)
        case "C":
            return(12)
        case "D":
            return(13)
        case "E":
            return(14)
        case "F":
            return(15)
            
def int2x(num):
    if num < 10:
        return(str(num))
        
    match num:
        case 10:
            return("A")
        case 11:
            return("B")
        case 12:
            return("C")
        case 13:
            return("D")
        case 14:
            return("E")
        case 15:
            return("F")
    
#CREATE TABLE modelinfo 
#    (modelname varchar(80), 
#    basemodel varchar(20), 
#    modeltype varchar(10), 
#    modeltrigger varchar(1000), 
#    modelcivurl varchar(100), 
#    modelhash varchar(10), 
#    modelid int, 
#    modelsteps int, 
#    modeldenoise varchar(200), 
#    modeleximageurl varchar(100), 
#    modelimageprompt varchar(1000), 
#    modellastused datetime primary key);



# read in the sage_cache.json file created by Sage Utils

tbcf = "7-100230004567-0"
Embed_Images = False
if len(sys.argv) > 1:
    passed = sys.argv[1]
    if len(passed) == 16:
        tbcf = passed
        if passed.endswith('1'):
            Embed_Images = True
        print("using custom output format: " + passed)
    else:
        print("Improper argument: " + passed)

nln = "\n"
comfy_base = pathlib.Path(folder_paths.base_path)
my_folder = comfy_base / "ComfyUI_Model-Catalog"
sc_path = comfy_base / "custom_nodes" / "ComfyUI_SageUtils" / "sage_cache.json"

start_time = time.perf_counter()
sage_cache = parse_json_file(sc_path)  # This will contain your parsed data if successful

cpdict = {}  # this is a container for checkpoint info

loradict = {}  # this is a container for lora info

print('# of Models: ' + str(len(sage_cache)))
num_models = len(sage_cache)
HIGHINT = 32000
all_models = sage_cache.keys() # returns a list of model full paths
# pathlib.Path.unlink("c:\\cui\\modelinfo.db")
conn = sqlite3.connect(":memory:") # create our sqlite3 db in memory
# conn = sqlite3.connect("c:\\cui\\modelinfo.db")  # create sqlite3 db on disk
cursor = conn.cursor()
cursor.execute("CREATE TABLE modelinfo (modelname varchar(80), basemodel varchar(20), modeltype varchar(10), modeltrigger varchar(1000), modelcivurl varchar(100), modelhash varchar(10), modelid int, modelsteps int, modeldenoise varchar(200), modeleximageurl varchar(100), modelimageprompt varchar(1000), modellastused datetime primary key);")
conn.commit()
i = 0
for curmodel in all_models: # loop through each model
    i = i + 1
    pctdone = int((i / num_models) * 100)
    print(f"Loading: {pctdone}%", end="\r")
    try:
        civitai = sage_cache[curmodel]['civitai']
    except Exception:
        civitai = "False"
    if civitai == "False":
        continue
    modeltrigger = ""
    basemodel = ""
    basemodel = sage_cache[curmodel]['baseModel']
    modeltype = sage_cache[curmodel]['model']['type']  # either Checkpoint or Lora
    
    modelname = sage_cache[curmodel]['model']['name']
    modelid = sage_cache[curmodel]['modelId']
    words = sage_cache[curmodel]['trainedWords']

    modeltrigger = ", ".join(words)
    
   
    modelhash = sage_cache[curmodel]['hash']
    try:
        modellastused = sage_cache[curmodel]['lastUsed']
    except Exception:
        modellastused = ""
        
    modelcivurl = "https://civitai.com/models/" + str(modelid)
#   print(f"..Processing: {modelname}")
    
#   print(f"....Pulling json for: {modelhash}")
    civjson = get_civitai_json(modelhash)
    if civjson == {}:
        print(f"....Unable to get data from {modelhash}. Continuing")
        continue
        
    foundeximage = False

    modeleximageurl = ""
    modelsteps = 0
    modelsampler = ""
    modelscheduler = ""
    modelcfgscale = 0
    modelimageprompt = ""
    for curimage in civjson['images']:
        try:
            imagesteps = curimage['meta']['steps']
        except Exception:
            imagesteps = 0
        
        if imagesteps > 0:                    
            foundeximage = True
            try:
                modeleximageurl = curimage['url']
            except Exception:
                modeleximageurl = ""
            try:
                modelsteps = curimage['meta']['steps']
            except Exception:
                modelsteps = 0
            try:
                modelsampler = curimage['meta']['sampler']
            except Exception:
                modelsampler = ""
            try:
                modelscheduler = curimage['meta']['scheduler']
            except Exception:
                modelscheduler = ""
            try:
                modelcfgscale = curimage['meta']['cfgScale']
            except Exception:
                modelcfgscale = 0
            try:
                modelimageprompt = curimage['meta']['prompt']
            except Exception:
                modelimageprompt = ""
            break
# if we didn't find an image with sampler/steps info go to a fallback image with at least a prompt            
    if foundeximage == False:
        for curimage in civjson['images']:
            try:
                modelimageprompt = curimage['meta']['prompt']
            except Exception:
                modelimageprompt = ""
                
            if modelimageprompt != "":
                foundeximage = True
                modeleximageurl = curimage['url']
                break
# if we didn't even find an image with a prompt, just grab image 0 as our example image                
        if foundeximage == False:
            try:
                modeleximageurl = civjson['images'][0]['url']
            except Exception:
                modeleximageurl = ""
                
            foundeximage = True
            
    modeleximageurl = modeleximageurl.replace("width=450", "width=200")
    modeltrigger = modeltrigger.replace(", ", ",")
    modeltrigger = modeltrigger.replace(",", ", ")
    modelimageprompt = modelimageprompt.replace(", ", ",")
    modelimageprompt = modelimageprompt.replace(",", ", ")
    modelimageprompt = modelimageprompt.replace("| ", "|")
    modelimageprompt = modelimageprompt.replace("|", "| ")
    modelimageprompt = modelimageprompt.replace("\r", "")
    modelimageprompt = modelimageprompt.replace("\n", "")
    modelimageprompt = modelimageprompt.replace('"', "")
    modelimageprompt = modelimageprompt.replace("'", "")
    
    if modeltype == "LoCon":
        modeltype = "LORA"
        
    if modellastused == "":    
        if modeltype == "LORA":
#           print(f"....Writing {modelname} to LORA dict") 
            loradict[curmodel] = {}
            loradict[curmodel]['modelname'] = modelname
            loradict[curmodel]['basemodel'] = basemodel  
            loradict[curmodel]['modeltype'] = modeltype             
            loradict[curmodel]['modeltrigger'] = modeltrigger
            loradict[curmodel]['modelcivurl'] = modelcivurl
            loradict[curmodel]['modeleximageurl'] = modeleximageurl
            loradict[curmodel]['modelsteps'] = modelsteps
            modeldenoise = "Steps: " + str(modelsteps) + "<br>" + "Sampler: " + modelsampler + "<br>" + "Scheduler: " + modelscheduler + "<br>" + "CFG Scale: " + str(modelcfgscale)
            loradict[curmodel]['modeldenoise'] = modeldenoise
            loradict[curmodel]['modelimageprompt'] = modelimageprompt
            loradict[curmodel]['modellastused'] = modellastused
            loradict[curmodel]['modelid'] = modelid
            loradict[curmodel]['modelhash'] = modelhash
        else:
#           print(f"....Writing {modelname} to checkpoint dict") 
            cpdict[curmodel] = {}
            cpdict[curmodel]['modelname'] = modelname
            cpdict[curmodel]['basemodel'] = basemodel 
            cpdict[curmodel]['modeltype'] = modeltype            
            cpdict[curmodel]['modeltrigger'] = modeltrigger
            cpdict[curmodel]['modelcivurl'] = modelcivurl
            cpdict[curmodel]['modeleximageurl'] = modeleximageurl
            cpdict[curmodel]['modelsteps'] = modelsteps
            modeldenoise = "Steps: " + str(modelsteps) + "<br>" + "Sampler: " + modelsampler + "<br>" + "Scheduler: " + modelscheduler + "<br>" + "CFG  Scale: " + str(modelcfgscale)
            cpdict[curmodel]['modeldenoise'] = modeldenoise
            cpdict[curmodel]['modelimageprompt'] = modelimageprompt
            cpdict[curmodel]['modellastused'] = modellastused
            cpdict[curmodel]['modelid'] = modelid
            cpdict[curmodel]['modelhash'] = modelhash
    else:       
        modeldenoise = "Steps: " + str(modelsteps) + "<br>" + "Sampler: " + modelsampler + "<br>" + "Scheduler: " + modelscheduler + "<br>" + "CFG Scale: " + str(modelcfgscale)
#       print(f"....Writing {modelname} to sqlite3 database")   
        cursor.execute("INSERT INTO modelinfo (modelname, basemodel, modeltype, modeltrigger, modelcivurl, modeleximageurl, modelsteps, modeldenoise, modelimageprompt, modellastused, modelid, modelhash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (modelname, basemodel, modeltype, modeltrigger, modelcivurl, modeleximageurl, modelsteps, modeldenoise, modelimageprompt, modellastused, modelid, modelhash))

conn.commit()
print("\n")
starthtml = "<!DOCTYPE html><html>\n<head><meta charset='utf-8'>\n<style>th {  border: 2px solid blue;  color: yellow; background-color: blue; font: 22px blue;}td {  border: 2px solid maroon;  font: 16px black;}</style>\n<script>async function copyToClipboard(text) {    try {    await navigator.clipboard.writeText(text);    console.log('Text copied to clipboard');  } catch (err) {    console.error('Failed to copy: ', err);  }}</script>\n</head><body><h1 align='center'>r3place</h1><table align='center'>   <tr> " 

column_heads = [
   '<th style="width:200px;"><b>Model Name</b></th>',
   '<th style="width:100px;"><b>Base Model</b></th>',
   '<th style="width:100px;"><b>Model Type</b></th>',
   '<th style="width:175px;"><b>Trigger Words</b></th>',
   '<th style="width:100px;"><b>Civitai URL</b></th>',
   '<th style="width:100px;"><b>Model Hash</b></th>',
   '<th style="width:100px;"><b>Model ID</b></th>',
   '<th style="width:100px;"><b>Model Steps</b></th>',
   '<th style="width:190px;"><b>Denoise settings</b></th>',
   '<th style="width:200px;"><b>Example Image</b></th>',
   '<th style="width:200px;"><b>Prompt used</b></th>',
   '<th style="width:100px;"><b>Last Model Use</b></th>' ]

   
                          
for mtype in ["LORA", "Checkpoint"]:
    totalhtml = starthtml.replace("r3place", mtype + " Details")
    maxcol = x2int(tbcf[0]) + 1
    for col in range (1, maxcol):
        fstr = int2x(col) 
        elm = tbcf.find(fstr, 2)
        if elm != -1:
            totalhtml += column_heads[elm-2]
        else:
            totalhtml += "<th></th>"
            
    totalhtml += "</tr>"
    dbselect = "SELECT * FROM modelinfo WHERE modeltype='" + mtype + "' order by modellastused DESC"
    
    cursor.execute(dbselect)  

    for row in cursor.fetchall():

        rowhtml = "<tr>"
        modelname = row[0]
        basemodel = row[1]
        modeltype = row[2]
        modeltrigger = row[3]
        modelcivurl = row[4]
        modelhash = row[5]
        modelid = row[6]
        modelsteps = row[7]
        modeldenoise = row[8]
        modeleximageurl = row[9]
        modelimageprompt = row[10]
        modellastused = row[11]
#       print(f"..Read {modelname} from sqlite3 db")
        denohtml = modeldenoise

        for col in range (1, maxcol):
            fstr = int2x(col) 
            elm = tbcf.find(fstr, 2)
            if elm != -1:
                elm = elm - 2
                match elm:
                    case 0:
                        if basemodel.startswith("Flux"):
                            rowhtml += '<td style="color:yellow;background-color:Tomato;text-align:center;">' + modelname + '</td>' + nln
                        else: 
                            if basemodel.startswith("Pony"):
                                rowhtml += '<td style="color:black;background-color:yellow;text-align:center;">' + modelname + '</td>' + nln
                            else:
                                if basemodel.startswith("SDXL"):
                                    rowhtml += '<td style="color:yellow;background-color:green;text-align:center;">' + modelname + '</td>' + nln
                                else:
                                    if basemodel.startswith("SD "):
                                        rowhtml += '<td style="color:white;background-color:black;text-align:center;">' + modelname + '</td>' + nln
                                    else:                                        
                                        rowhtml += '<td style="color:black;background-color:red;text-align:center;">' + modelname + '</td>' + nln
                    case 1:
                        rowhtml += '<td style="text-align:center;">' + basemodel + '</td>' + nln
                    case 2:
                        rowhtml += '<td style="text-align:center;">' + modeltype + '</td>' + nln
                    case 3:
                        if modeltrigger == "":
                            rowhtml += '<td style="text-align:center;"><i>No triggers</i></td>' + nln
                        else:
                            rowhtml += '<td style="text-align:center;">' + modeltrigger + '<br><br><button style="background-color: #01006D; color: yellow;" id="copyButton" onclick="copyToClipboard(' + "'" + modeltrigger + "'" + ')">Triggers to clipboard</button></td>' + nln
                    case 4:
                        rowhtml += '<td style="text-align:center;"><a href="' + modelcivurl + '">' + str(modelid) + '</a></td>' + nln
                    case 5:
                        rowhtml += '<td style="text-align:center;">' + modelhash + '</td>' + nln
                    case 6:
                        rowhtml += '<td style="text-align:center;">' + str(modelid) + '</td>' + nln
                    case 7:
                        rowhtml += '<td style="text-align:center;">' + str(modelsteps) + '</td>' + nln
                    case 8:
                        if modelsteps > 14 or modelsteps == 0:                        
                            rowhtml += '<td style="text-align:center;">' + denohtml + '</td>' + nln
                        else:
                            rowhtml += '<td style="color:yellow;background-color:black;text-align:center;">' + denohtml + '</td>' + nln
                    case 9:
                        if Embed_Images == True:
                            fname = getFNfromURL(modeleximageurl)
                            ofname = my_folder / "images" / fname
#                           print(f"retrieving {modeleximageurl} to {ofname}")
                            
                            download_image(modeleximageurl, ofname) 
  
                            rowhtml += '<td style="text-align:center;"><img src="' + str(ofname) + '"></td>' + nln
                        else:
                            rowhtml += '<td style="text-align:center;"><img src="' + modeleximageurl + '"></td>' + nln
                            
                    case 10:
                        if modelimageprompt == "":
                            rowhtml += "<td></td>" + nln
                        else:
                            rowhtml += '<td style="text-align:center;">' + modelimageprompt + '<br><br><button style="background-color: #01006D; color: yellow;" id="copyButton" onclick="copyToClipboard(' + "'" + modelimageprompt + "'" + ')">Prompt to clipboard</button></td>' + nln
                    case 11:
                        rowhtml += '<td style="text-align:center;">' + modellastused + '</td>' + nln
            else:
                rowhtml += "<td></td>"
                        
        rowhtml += "</tr>"

        totalhtml += rowhtml
    if mtype == "LORA":
        modeld = loradict
    else:
        modeld = cpdict
        
    all_models = modeld.keys()                          # returns a list of model full paths
    for curmodel in all_models:
        modeltype = modeld[curmodel]['modeltype']
        if modeltype != mtype:
            continue
        modelname = modeld[curmodel]['modelname']
        modeltrigger = modeld[curmodel]['modeltrigger']
        modelcivurl = modeld[curmodel]['modelcivurl']
        modeleximageurl = modeld[curmodel]['modeleximageurl']
        modelsteps = modeld[curmodel]['modelsteps']
        modeldenoise = modeld[curmodel]['modeldenoise']
        modelimageprompt = modeld[curmodel]['modelimageprompt']
        modelid = modeld[curmodel]['modelid']
        modelname = modeld[curmodel]['modelname']
        modelhash = modeld[curmodel]['modelhash']
        basemodel = modeld[curmodel]['basemodel']
        modellastused = ""
        rowhtml = "<tr>"

        denohtml = modeldenoise

        for col in range (1, maxcol):
            fstr = int2x(col) 
            elm = tbcf.find(fstr, 2)
            if elm != -1:
                elm = elm - 2
                match elm:
                    case 0:
                        if basemodel.startswith("Flux"):
                            rowhtml += '<td style="color:yellow;background-color:Tomato;text-align:center;">' + modelname + '</td>' + nln
                        else: 
                            if basemodel.startswith("Pony"):
                                rowhtml += '<td style="color:black;background-color:yellow;text-align:center;">' + modelname + '</td>' + nln
                            else:
                                if basemodel.startswith("SDXL"):
                                    rowhtml += '<td style="color:yellow;background-color:green;text-align:center;">' + modelname + '</td>' + nln
                                else:
                                    if basemodel.startswith("SD "):
                                        rowhtml += '<td style="color:white;background-color:black;text-align:center;">' + modelname + '</td>' + nln
                                    else:                                        
                                        rowhtml += '<td style="color:black;background-color:red;text-align:center;">' + modelname + '</td>' + nln
                    case 1:
                        rowhtml += '<td style="text-align:center;">' + basemodel + '</td>' + nln
                    case 2:
                        rowhtml += '<td style="text-align:center;">' + modeltype + '</td>' + nln
                    case 3:
                        if modeltrigger == "":
                            rowhtml += '<td style="text-align:center;"><i>No triggers</i></td>' + nln
                        else:
                            rowhtml += '<td style="text-align:center;">' + modeltrigger + '<br><br><button style="background-color: #01006D; color: yellow;" id="copyButton" onclick="copyToClipboard(' + "'" + modeltrigger + "'" + ')">Triggers to clipboard</button></td>' + nln
                    case 4:
                        rowhtml += '<td style="text-align:center;"><a href="' + modelcivurl + '">' + str(modelid) + '</a></td>' + nln
                    case 5:
                        rowhtml += '<td style="text-align:center;">' + modelhash + '</td>' + nln
                    case 6:
                        rowhtml += '<td style="text-align:center;">' + str(modelid) + '</td>' + nln
                    case 7:
                        rowhtml += '<td style="text-align:center;">' + str(modelsteps) + '</td>' + nln
                    case 8:
                        if modelsteps > 14 or modelsteps == 0:                        
                            rowhtml += '<td style="text-align:center;">' + denohtml + '</td>' + nln
                        else:
                            rowhtml += '<td style="color:yellow;background-color:black;text-align:center;">' + denohtml + '</td>' + nln
                    case 9:
                        if Embed_Images == True:
                            fname = getFNfromURL(modeleximageurl)
                            ofname = my_folder / "images" / fname
#                           print(f"retrieving {modeleximageurl} to {ofname}")
                            
                            download_image(modeleximageurl, ofname) 
  
                            rowhtml += '<td style="text-align:center;"><img src="' + str(ofname) + '"></td>' + nln
                        else:
                            rowhtml += '<td style="text-align:center;"><img src="' + modeleximageurl + '"></td>' + nln
                            
                    case 10:
                        if modelimageprompt == "":
                            rowhtml += "<td></td>" + nln
                        else:
                            rowhtml += '<td style="text-align:center;">' + modelimageprompt + '<br><br><button style="background-color: #01006D; color: yellow;" id="copyButton" onclick="copyToClipboard(' + "'" + modelimageprompt + "'" + ')">Prompt to clipboard</button></td>' + nln
                    case 11:
                        rowhtml += '<td style="text-align:center;">' + modellastused + '</td>' + nln
            else:
                rowhtml += "<td></td>"
                        
        rowhtml += "</tr>"
        totalhtml += rowhtml        
  
    totalhtml += '</table></body></html>'
    print("\n")
    if mtype == "LORA":
        outfile = open(my_folder / "loras.html", "w", encoding="utf-8") 
        outfile.write(totalhtml)
        outfile.close()
    else:
        outfile = open(my_folder / "xpoints.html", "w", encoding="utf-8") 
        outfile.write(totalhtml)
        outfile.close()
end_time = time.perf_counter()
elapsed = end_time - start_time
print("Elapsed time=" + str(elapsed))
cursor.close()
conn.close
