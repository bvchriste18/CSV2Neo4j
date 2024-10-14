# CSV2Neo4j
This is an example project to describe how to load a csv file (merge_split.csv) created from [ASSET](https://doi.org/10.1016/j.compfluid.2023.105808) into a graph database on Neo4j desktop. The output is a neo4j graph database with droplets labelled by breakup stage and connected by splits and merges. 

## Setup/Running the Script
First, you need to install the desktop version of Neo4j. Found [here](https://neo4j.com/download/?utm_source=Google&utm_medium=PaidSearch&utm_campaign=Evergreen&utm_content=AMS-Search-SEMCE-DSA-None-SEM-SEM-NonABM&utm_term=&utm_adgroup=pmax&gad_source=1&gclid=CjwKCAjw6c63BhAiEiwAF0EH1Ay5vc5tWtd01RVUDIpBCwSmwvaxg_XNPzxMZyQy3cMirWZHrMQROBoCo38QAvD_BwE).

When the desktop app is installed, create a new project:

![new_project](https://github.com/user-attachments/assets/8cb61573-e0e5-46ba-8607-6dce25f1cda2)

Then, create a local DBMS:

![new_dbms](https://github.com/user-attachments/assets/221ff78a-2063-47c1-a1d9-37fead7255be)

Install the APOC library on this DBMS:

![install_apoc](https://github.com/user-attachments/assets/1569e6ea-c3a3-4aaf-bc56-64d794c7d986)

Next, locate the "import" folder for this DBMS:

![image](https://github.com/user-attachments/assets/d3f85189-2913-40eb-b0d5-80ad3643d6c9)

Copy your merge_split.csv file into this folder.

Now, start the DBMS:

![start_dbms](https://github.com/user-attachments/assets/125bf831-1574-431d-a7fe-09a2ebedc128)

Finally, adjust the names/parameters in the python script "import.py" and run the script.

To see if the script executed properly, open the neo4j browser (the blue "open" button) and you should see something like this on the left-hand side:

![image](https://github.com/user-attachments/assets/72856f4b-cc91-4796-90ea-ad10a165e655)

**Note:** If anything goes wrong while the script is running, you should run
```
match(n)
detach delete n
```
to delete any data already read in before attempting to load the csv again. 

## Other analysis scripts

The neo4j python API allows for parsing and gathering data directly from the graph database. The example "weber_calc.py" shows how you can run queries in the python script to accomplish this. This script looks for two sets of data, one, droplets that breakup further and the other droplets that do not break up further in the simulation, it then calculates the weber number from gas and liquid velocities extracted using ASSET.

## Notes for NGA2
The workflow for csv files derived from NGA2 is mostly the same. The only difference is that csv files from NGA2 must be formatted first to remove excess spaces. This can be done with the clean_csv.py script before uploading the csv file into the import directory. 

## Additional Notes

Sometimes these csv files are large. You might run into the error: ```The memory pool limit was exceeded.```

If you do, you need to locate the neo4j.conf file, which you can find the same way you found the import folder, but navigate to the configuration folder. Open neo4j.conf and scroll to the bottom. You should see the following:

![image](https://github.com/user-attachments/assets/201ad27d-03f9-42ee-983f-f096d43f3178)

Change ```dbms.memory.heap.max_size=1G``` to 4G (Note: you may need to adjust these depending on your system). 


If you want to output a csv file from the newly labelled data, you have to first create an 'apoc.conf' file in the dbms configuration folder and in that file, write:
```bash
apoc.export.file.enabled=true
```
Then, the command can be typed into the cypher command line as:
```bash
CALL apoc.export.csv.all("filename.csv", {})
```
