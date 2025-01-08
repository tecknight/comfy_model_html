 make_model_html.py  
 this program reads the **sage_cache.json**, pulls more data from civitai, then writes out models that hava a lastused timestamp to a sqlite3 database in memory
 it writes out models that do not have a last used timestamp to internal dictionaries. It then uses these data sources to create 2 html files.
 - **loras.html** contains all comfyui loras starting with the most recently used
 - **xpoints.html** contains all comfyUI checkpoints starting with the most recently used  
 here is an example: <https://aiartalley.com/xpoints.html>  
 ![checkpoint report image](checkpoints.png)
 The format and composition of the html tables can be customized as follows
 You can customize the output table format completely.
 You can add fields, remove fields, change the column order, whatever you like    
 Number indicates which column in table, zero means do not include this field
 If you need 10 or more columns use hex (A = 10, B = 11, etc)       
 A 14 character formatted string can be passed as a shell parameter:

                      +-Embed Images (0=False, 1=True). If True will download images locally, making completely offline pages
                      |
       7-100230004567-0
       | |||||||||||└- Last used date 
	   | ||||||||||└-- Prompt
	   | |||||||||└--- Example image
	   | ||||||||└---- Denoise info
	   | |||||||└----- Steps used——
	   | ||||||└------ Model civitai ID
	   | |||||└------- Model hash
	   | ||||└-------- Civitai URL
	   | |||└--------- Trigger words
	   | ||└---------- Model type (LORA or Checkpoint)
	   | |└----------- Base model (Flux, Pony, etc)
	   | └------------ Model name
	   └-------------- Number of columns

 The example and default string tells the program to create a 7 column table containing:
 - Model name in column 1
 - Trigger words in column 2
 - Civitai URL in column 3
 - Denoise info in column 4
 - Example image in column 5
 - Prompt in column 6
 - Last used date in column 7