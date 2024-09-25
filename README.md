# CSV2Neo4j
This is an example project to describe how to load a csv file (merge_split.csv) created from [ASSET](https://doi.org/10.1016/j.compfluid.2023.105808) into a graph database on Neo4j desktop.

# Setup/Running the Script
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

# Additional Notes

Sometimes these csv files (like the one included here as an example) are large. You might run into the error:

```bash
The memory pool limit was exceeded.
```
If you do, you need to locate the neo4j.conf file, which you can find the same way you found the import folder, but navigate to the configuration folder. Open neo4j.conf and scroll to the bottom. You should see the following:

![image](https://github.com/user-attachments/assets/201ad27d-03f9-42ee-983f-f096d43f3178)

Change dbms.memory.heap.max_size=1G to 4G (Note: you may need to adjust these depending on your system). 

