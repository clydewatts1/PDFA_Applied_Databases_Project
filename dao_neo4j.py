import main as main
import logging

# setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

url = "bolt://localhost:7687"
username = "neo4j"
password = "neo4jneo4j"

dao_neo4j = main.DAO_Neo4j(uri=url, user=username, password=password)

_, err = dao_neo4j.connect()
if err:
    logging.error(f"*** ERROR *** Connecting to Neo4j: ({err.errno}, \"{err.msg}\")")

results, err = dao_neo4j.get_all_attendees()
if err:
    logging.error(f"*** ERROR *** Getting connected attendees: ({err}")
#print(results)
results,err = dao_neo4j.get_connected_attendees("101")
if err:
    logging.error(f"*** ERROR *** Getting connected attendees: ({err})")
print("Connected Attendees for AttendeeID 101:")
for record in results:
    logging.info(f"Connected AttendeeID: {record['connected.AttendeeID']}")
dao_neo4j.close()

