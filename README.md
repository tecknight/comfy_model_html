 # make_model_html.py 
 ****
  This program requires that the **EXTREMELY USEFUL** ComfyUI custom node **Sage Utils**:  
 <https://github.com/arcum42/ComfyUI_SageUtils> be installed.  
 In addition to enabling the model tables provided by this utility, Sage Utils provides several additional features. It makes sure your images have all metadata needed so you can recreate them and civitai will recognise them as well. It also allows you to optionally add additional custom metadata, and is able to recognise even renamed models based upon their SHA256 hash. It also keeps track of when each model was last used, enabling some additional features. It's #1611 under custom nodes in ComfyUI Manager.   
 this program reads the **sage_cache.json**, pulls more data from civitai, then writes out models that hava a lastused timestamp to a sqlite3 database in memory
 it writes out models that do not have a last used timestamp to internal dictionaries. It then uses these data sources to create 2 html files.
 - **loras.html** contains all comfyui loras starting with the most recently used
 - **xpoints.html** contains all comfyUI checkpoints starting with the most recently used  
 here is an example: <https://aiartalley.com/xpoints.html>  
 
 ![checkpoint report screencap](checkpoints.png)
 ****
 The format and composition of the html tables can be customized as follows:  
 You can customize the output table format completely.  
 You can add fields, remove fields, change the column order, whatever you like.    
 Number indicates which column in table, zero means do not include this field.  
 If you need 10 or more columns use hex (A = 10, B = 11, etc).        
 A 16 character formatted string can be passed as a shell parameter:  

                      ┌──►Embed Images (0=False, 1=True). If True, will download 
                      │  images and save locally, making offline pages
                      │
       8-120340005678-0
       │ │││││││││││└─►Last used timestamp 
	   │ ││││││││││└─►Prompt
	   │ │││││││││└─►Example image
	   │ ││││││││└─►Denoise info (steps, sampler, scheduler and config scale)
	   │ │││││││└─►# of Steps used
	   │ ││││││└─►Model civitai ID
	   │ │││││└─►Model hash
	   │ ││││└─►Civitai URL
	   │ │││└─►Trigger words
	   │ ││└─►Model type (LORA or Checkpoint)
	   │ │└─►Base model (Flux, Pony, etc)
	   │ └─►Model name
	   └──►Number of columns

 The example and default string as shown above tells the program to create:  
 An 8 column table with:
 - *Model name* in column 1
 - *Base model* in column 2
 - *Trigger words* in column 3
 - *Civitai URL* in column 4
 - *Denoise info* in column 5
 - *Example image* in column 6
 - *Prompt* in column 7
 - *Last used timestamp* in column 8
 - Images are *not* embedded, and are linked as URLs