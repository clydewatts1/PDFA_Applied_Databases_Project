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

logging.info("Resetting Neo4j database...")
_, err = dao_neo4j.delete_all_nodes_and_relationships()
logging.info("Neo4j database reset successfully.")
if err:
    logging.error(f"*** ERROR *** Deleting all nodes and relationships: ({err})")
dao_neo4j.merge_attendee(101)
if err:
    logging.error(f"*** ERROR *** Deleting all nodes and relationships: ({err})")
logging.info("Attendee 101 merged successfully.")
dao_neo4j.merge_attendee(102)
dao_neo4j.merge_attendee(103)
dao_neo4j.merge_attendee(104)
dao_neo4j.merge_attendee(105)
dao_neo4j.merge_attendee(106)
dao_neo4j.merge_attendee(107)
dao_neo4j.merge_attendee(108)
dao_neo4j.merge_attendee(109)
dao_neo4j.merge_attendee(110)
dao_neo4j.merge_attendee(111)
dao_neo4j.merge_attendee(113)
dao_neo4j.merge_attendee(114)
dao_neo4j.merge_attendee(115)
dao_neo4j.merge_attendee(116)
dao_neo4j.merge_attendee(117)
dao_neo4j.merge_attendee(118)
dao_neo4j.merge_attendee(120)
dao_neo4j.merge_connection(101, 109)
dao_neo4j.merge_connection(101, 107)
dao_neo4j.merge_connection(102, 110)
dao_neo4j.merge_connection(103, 111)
dao_neo4j.merge_connection(104, 120)
dao_neo4j.merge_connection(105, 113)
dao_neo4j.merge_connection(106, 114)
dao_neo4j.merge_connection(107, 115)
dao_neo4j.merge_connection(108, 116)
dao_neo4j.merge_connection(111, 101)
dao_neo4j.merge_connection(106, 103)
dao_neo4j.merge_connection(120, 103)
dao_neo4j.close()

