# make_model_html.py  
 This program requires that the **EXTREMELY USEFUL** ComfyUI custom node **Sage Utils** <https://github.com/arcum42/ComfyUI_SageUtils> be installed.
 **comfy_model_html** reads the SageUtils **sage_cache.json**, pulls additional model data from civitai, then writes out models that have a lastused timestamp to a sqlite3 database in memory.
 It then writes out models that do not have a last used timestamp to internal dictionaries in memory. It uses these data sources to create 2 html files:
 - **loras.html** details all comfyUI loras starting with the most recently used
 - **xpoints.html** details all comfyUI checkpoints starting with the most recently used  
 Here is an example: <https://aiartalley.com/xpoints.html>  
 
 The format and composition of the html tables can be customized.
 You can specify the output table format, specifying which fields you want in the table and the column order you prefer.
 A 14 character formatted string can be passed as a shell parameter
 The first character indicates the total total number of columns in your table
 The 3rd through the last character indicate the destination of each data field, 0 means the field is not displayed in the output table.
 Any other value indicates the column number to display the field in.
 If you need 10 or more columns use hex (A = 10, B = 11, etc)       
 :

       7-100230004567
       | |||||||||||└- Last used date 
	   | ||||||||||└-- Prompt
	   | |||||||||└--- Example image
	   | ||||||||└---- Denoise info
	   | |||||||└----- Steps used
	   | ||||||└------ Model civitai ID
	   | |||||└------- Model hash
	   | ||||└-------- Civitai URL
	   | |||└--------- Trigger words
	   | ||└---------- Model type (LORA or Checkpoint)
	   | |└----------- Base model (Flux, Pony, etc)
	   | └------------ Model name
	   └-------------- Number of columns

 The example and default string tells the program to create a 7 column table containing:
 - *Model name* in column 1
 - *Trigger words* in column 2
 - *Civitai URL* in column 3
 - *Denoise info* in column 4
 - *Example image* in column 5
 - *Prompt* in column 6
 - *Last used date* in column 7
