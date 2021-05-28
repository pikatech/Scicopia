import logging
import sys

from pyArango.collection import Collection, Edges, Field
from pyArango.database import Database
from pyArango.graph import EdgeDefinition, Graph
from tqdm import tqdm

from scicopia.config import read_config
from scicopia.exceptions import ScicopiaException
from scicopia.utils.arangodb import connect, get_docs, select_db

logger = logging.getLogger("scicopia")
logger.setLevel(logging.INFO)


def create_graph(docs: Collection, database: Database):
    # Workaround for "ValueError: 'name' is not a defined Collections"
    Collection.collectionClasses[docs.name] = type(docs)

    class DocLinks(Edges):

        _fields = {"direction": Field()}

    class Citations(Graph):

        _edgeDefinitions = [
            EdgeDefinition(
                "DocLinks", fromCollections=[docs.name], toCollections=[docs.name]
            )
        ]
        _orphanedCollections = []

    if database.hasCollection("DocLinks"):
        logger.warning("Collection DocLinks already existed, dropping it.")
        edges = database["DocLinks"]
        edges.delete()
    edges = database.createCollection("DocLinks")
    if database.hasGraph("Citations"):
        logger.warning("Graph Citations already existed, dropping it.")
        graph = database.graphs["Citations"]
        graph.delete()
    graph = database.createGraph("Citations")
    link_works(edges, docs, graph, database)


def link_works(edges: Collection, docs: Collection, graph: Graph, db: Database):
    links = {"citing": f"FOR x IN {docs.name} FILTER (x.citing != null) RETURN {{key: x._key, links: x.citing}}",
           "cited-by": f"FOR x IN {docs.name} FILTER (x.cited_by != null) RETURN {{key: x._key, links: x.cited_by}}"}
    BATCHSIZE = 100
    TTL = BATCHSIZE * 10  # Time-to-live
    for direction, aql in links.items():
        query = db.AQLQuery(aql, rawResults=True, batchSize=BATCHSIZE, ttl=TTL)
        todo = (
            query.response["extra"]["stats"]["scannedFull"]
            - query.response["extra"]["stats"]["filtered"]
        )
        logging.info(f"{todo} documents in found.")
        for doc in tqdm(query):
            works = [link.strip() for link in doc["links"].split(",")]
            for work in works:
                if work in docs:
                    graph.createEdge(
                        edges.name,
                        f"{docs.name}/{doc['key']}",
                        f"{docs.name}/{work}",
                        edgeAttributes={"direction": direction},
                    )
                else:
                    logger.warning("Invalid citation in %s: %s", doc["key"], work)


if __name__ == "__main__":
    config = read_config()
    try:
        conn = connect(config)
        db = select_db(config, conn)
        docs = get_docs(config, db)
        create_graph(docs, db)
    except ScicopiaException as e:
        logger.error(e)
        sys.exit(2)
