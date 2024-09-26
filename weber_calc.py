from neo4j import GraphDatabase
import numpy as np
import matplotlib.pyplot as plt

# Connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "brendan1"

# Connect to the database
driver = GraphDatabase.driver(uri, auth=(user, password))

# Constants for calculation
rho_gas = 1.226  # Gas Density
sigma = 0.0728  # Surface Tension Coefficient

# Queries to fetch nodes
query1 = """
MATCH (n)
WHERE NOT (n:core) AND (n)-[:Split]->() 
RETURN n.U AS u, n.V AS v, n.W AS w, n.U_gas AS u_gas, n.V_gas AS v_gas, n.W_gas AS w_gas, n.Volume AS volume
"""

query2 = """
MATCH (n)
WHERE NOT (n)-[:Split]->() AND NOT (n:core)
RETURN n.U AS u, n.V AS v, n.W AS w, n.U_gas AS u_gas, n.V_gas AS v_gas, n.W_gas AS w_gas, n.Volume AS volume
"""

# Function to execute queries and fetch results
def fetch_nodes(session, query):
    result = session.run(query)
    return [record.data() for record in result]

# Function to calculate Weber numbers
def calculate_weber_numbers(nodes):
    weber_numbers = []
    for node in nodes:
        if node['volume'] >= (1.33e-4)**3:
            U_slip = np.sqrt((node['u'] - node['u_gas'])**2 + (node['v'] - node['v_gas'])**2 + (node['w'] - node['w_gas'])**2)
            D_eq = (6 * node['volume'] / np.pi)**(1/3)
            Weber = rho_gas * U_slip**2 * D_eq / sigma
            Weber = np.log10(Weber)
            weber_numbers.append(Weber)
        
    return weber_numbers

# Start the session and run queries
with driver.session() as session:
    nodes_with_split = fetch_nodes(session, query1)
    nodes_without_split = fetch_nodes(session, query2)

# Calculate Weber numbers
we_int = calculate_weber_numbers(nodes_with_split)
we_final = calculate_weber_numbers(nodes_without_split)

# Plotting overlaid histograms
bins = np.histogram(np.hstack((we_int, we_final)), bins=40)[1]  # get the bin edges
plt.figure(figsize=(10, 6))
plt.hist(we_int, bins=bins, alpha=0.5, label='Breaks up Further', color='#377eb8', edgecolor='black', density=True)
plt.hist(we_final, bins=bins, alpha=0.5, label='Does not Break up Further', color='#ff7f00', edgecolor='black', density=True)
plt.title('Comparison of Weber Numbers')
plt.xlabel('Weber Number')
plt.ylabel('Frequency')
plt.legend()
plt.show()

# Close the driver connection
driver.close()


