from neo4j import GraphDatabase

'''
Steps to take atomization data from a merge_split.csv file created by ASSET
1. Start Neo4j and create a new database and local dbms
2. Move merge_split.csv file into the 'import' directory in your new dbms
3. Activate APOC in your DBMS
4. Start the dbms
5. Rename the relevant parameters below
6. Run the script
'''
'''
NOTE: Current version requires that merge events be input on separate lines
IN CSV FILE. e.g. if 4 and 5 merge into 6, the rows should be:
   | EventType, OldID, NewID, ...|
   | Merge    , 4    , 6    , ...|
   | Merge    , 5    , 6    , ...|
If NGA2 is not currently set up to output data like this,
the cleanup script clean_csv.py can be used to prepare the csv
'''

# Connect to your Neo4j database !!! RENAME DEPENDING ON YOUR DBMS !!!
uri = "neo4j://localhost:7687"
username = "neo4j"
password = "12345678"  # replace with your password

# Create driver instance
driver = GraphDatabase.driver(uri, auth=(username, password))

# Function to execute a Cypher query
def execute_query(session, query):
    result = session.run(query)
    summary = result.consume()
    avail = summary.result_available_after
    cons = summary.result_consumed_after
    total_time = avail + cons
    print(f"Query executed: {query[:50]}... | Execution Time: {total_time} ms")

# Step 1: Load CSV and create nodes 
# !!! ADJUST PARAMETERS DEPENDING ON YOUR MERGE_SPLIT FILE !!!
def load_csv_and_create_nodes(session):
    query = """
    LOAD CSV WITH HEADERS FROM "file:///updated_merge_split.csv" AS csvline
    CALL {
    WITH csvline
    CREATE (n:droplet { 
        id: toInteger(csvline.NewID),
        Event: csvline.EventType,
        OldID: toInteger(csvline.OldIDs),
        NewID: toInteger(csvline.NewID),
        Volume: toFloat(csvline.NewVol),
        Event_Time: toFloat(csvline.Time),
        X: toFloat(csvline.X),
        Y: toFloat(csvline.Y),
        Z: toFloat(csvline.Z),
        U: toFloat(csvline.U),
        V: toFloat(csvline.V),
        W: toFloat(csvline.W),
        L1: toFloat(csvline.L1),
        L2: toFloat(csvline.L2),
        L3: toFloat(csvline.L3)
    })
    } IN TRANSACTIONS OF 10000 ROWS;
    """


    execute_query(session, query)


# TO-DO - GENERALIZE CODE FOR ARBITRARY NUMBER OF LIQUID CORES
# INITIALIZE NODES TO ENSURE EVERY OLDID HAS A NEWID AT SOME POINT

# def initialize_nodes(session):
#     query = """
#     MATCH (n)
#     WHERE AND NOT EXISTS {
#     MATCH (d)
#     WHERE d.NewID = oldID
#     AND NOT oldID IN d.OldIDs
#     }
#     with distinct oldID
#     // Create a new node
#     CREATE (n:droplet{Event:'None',NewID:oldID,OldIDs:oldID,Volume:1.0})
#     RETURN n
#     """
#     execute_query(session, query)


# Step 2: Create Merge Relations
def create_merge_relations(session):
    # Find Merges between droplets, but not liquid core yet
    query1 = """
    MATCH (m:droplet {Event: "Merge"}),(d:droplet)
    WHERE d.NewID = m.OldID and m.NewID <> 1 
    CREATE (d)-[:Merge]->(m)
    """
    execute_query(session, query1)

    # Merge together separate merge nodes into one
    query2 = """ 
    MATCH (n:droplet{Event:"Merge"})
    WHERE n.NewID <> 1 
    WITH n.NewID as NewID, COLLECT(n) AS nodes
    WHERE size(nodes) > 1
    CALL apoc.refactor.mergeNodes(nodes,{
        id:'discard',
        Event: 'discard',
        OldID: 'combine',
        NewID: 'discard',
        Volume: 'discard',
        Event_Time: 'discard',
        X: 'discard',
        Y: 'discard',
        Z: 'discard',
        U: 'discard',
        V: 'discard',
        W: 'discard',
        L1: 'discard',
        L2: 'discard',
        L3: 'discard'
    })
    YIELD node
    RETURN node
    """
    execute_query(session, query2)
    
    # Merging nodes together produce some repeat relationships 
    # where (d:merge)-[merge]->(n:merge)
    # Remove all but the first merge relation between nodes
    query3 = """
    match(n:droplet{Event:'Merge'})-[r]->(d:droplet{Event:'Merge'})
    WITH d, n, collect(r) as rels
    WHERE size(rels)>1
    FOREACH (r in rels[1..] | DELETE r)
    """
    execute_query(session, query3)
    
    # Find merges with core
    query4 = """
    MATCH (n:droplet{Event:"None"}),(d:droplet),(m:droplet{Event:"Merge"})
    WHERE n.NewLID = m.NewLID AND d.NewLID = m.OldLID
    CREATE (d)-[:Merge]->(n)
    """
    execute_query(session, query4)
    
    # Delete nodes that represent struct merging with core    
    query5 = """
    MATCH (m:droplet {Event: "Merge"}),(n:droplet{Event:"None"})
    WHERE m.NewID = n.NewID 
    delete m
    """    
    execute_query(session, query5)


# Step 4: Create Split Relations
def create_split_relations(session):
    query = """
    MATCH (n:droplet {Event: "Split"}), (d:droplet)
    WHERE n.OldID = d.NewID
    CREATE (d)-[:Split]->(n)
    """
    execute_query(session, query)

# Step 5: Delete "Out of Domain" Nodes
def delete_out_of_domain_nodes(session):
    query = """
    MATCH (n:droplet)
    WHERE n.Event = "Out of Domain"
    DETACH DELETE n
    """
    execute_query(session, query)

# Function to rename nodes
def rename_labels(session, label_match, label_new, condition):
    query = f"""
    MATCH (n:{label_match})
    WHERE {condition}
    WITH collect(n) as p
    CALL apoc.refactor.rename.label("droplet","{label_new}",p)
    YIELD committedOperations
    RETURN committedOperations
    """
    execute_query(session, query)

# Function to rename remaining droplet nodes
def rename_remaining_nodes(session, current_label, next_label):
    query = f"""
    MATCH (n:droplet),(d:`{current_label}`)
    WHERE ANY(id IN n.OldIDs WHERE id = d.NewID)
    WITH collect(n) as p
    CALL apoc.refactor.rename.label("droplet","{next_label}",p)
    YIELD committedOperations
    RETURN committedOperations
    """
    execute_query(session, query)

# Main
with driver.session() as session:
    load_csv_and_create_nodes(session)
    #initialize_nodes(session)
    create_merge_relations(session)
    create_split_relations(session)
    delete_out_of_domain_nodes(session)
    
    # Renaming labels
    rename_labels(session,'droplet','core','n.Event="None"')
    rename_labels(session,'droplet{Event:"Split"}','primary','n.OldID=1')

    # TO-DO - NEED SOME SCHEME TO DETERMINE BREAKUP STAGES
    
# Close the driver connection
driver.close()

'''
Other helpful commands:
    
To delete full database in batches (for large databases):

call apoc.periodic.iterate(
    "MATCH (m) RETURN m", 
    "DETACH DELETE m",
    {batchSize:10000,parallel:true})
'''