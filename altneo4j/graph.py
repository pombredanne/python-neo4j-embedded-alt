from itertools import imap
from contextlib import contextmanager

import jpype

from java import DynamicRelationshipType
from java import GlobalGraphOperations
from java import EmbeddedGraphDatabase
from java import Direction


class Element(object):

    @property
    def id(self):
        return self._element.getId()

    def __getitem__(self, key):
        return self._element.getProperty(key)

    def __setitem__(self, key, value):
        self._element.setProperty(key, value)

    def items(self):
        return self._element.items()

    def keys(self):
        return self._element.getPropertyKeys()

    def values(self):
        return self._element.getPropertyValues()

    def __eq__(self, other):
        return self.id == other.id

    def delete(self):
        self._element.delete()


class Relationship(Element):

    def __init__(self, relationship):
        self._element = relationship

    def type(self):
        return self._element.getType().name()

    def start(self):
        return Node(self._element.getStartNode())

    def end(self):
        return Node(self._element.getEndNode())


class NodeRelationships(object):

    def __init__(self, node):
        self._node = node

    def both(self):
        return imap(Relationship, self._node.getRelationships())

    def __relationship(self, direction, type):
        if type:
            type = DynamicRelationshipType.withName(type)
            iterator = self._node.getRelationships(direction, type)
            iterator = iterator.iterator()
        else:
            iterator = self._node.getRelationships(direction)
            iterator = iterator.iterator()
        return imap(Relationship, iterator)

    def outgoing(self, type=None):
        return self.__relationship(Direction.OUTGOING, type)

    def incoming(self, type=None):
        return self.__relationship(Direction.INCOMING, type)


class Node(Element):

    def __init__(self, node):
        self._element = node
        self.relationships = NodeRelationships(self._element)

    def __getattr__(self, attr):
        type = DynamicRelationshipType.withName(attr)
        def create_relationship(node):
            rel = self._element.createRelationshipTo(node._element, type)
            return Relationship(rel)
        return create_relationship


class Nodes(object):

    def __init__(self, db, operations):
        self._db = db
        self._operations = operations

    @property
    def index():
        raise NotImplemented

    def __call__(self):
        iterator = self._operations.getAllNodes().iterator()
        return imap(Node, iterator)

    def __len__(self):
        return len(list(self))

    def get(self, id):
        return Node(self._db.getNodeById(long(id)))


class Relationships(object):

    def __init__(self, db, operations):
        self._db = db
        self._operations = operations

    @property
    def indexes():
        raise NotImplemented

    def __call__(self):
        iterator = self._operations.getAllRelationships().iterator()
        return imap(Relationship, iterator)

    def types(self):
        return self.__operations.getAllRelationshipTypes()

    def __len__(self):
        return len(list(self))

    def get(self, id):
        return Relationship(self._db.getRelationshipById(long(id)))


class GraphDB(object):

    def __init__(self, path):
        jpype.attachThreadToJVM()
        jpype.java.lang.System.setProperty("neo4j.ext.udc.source", "altneo4j")
        self._db = EmbeddedGraphDatabase(path)
        operations = GlobalGraphOperations.at(self._db)
        self.nodes = Nodes(self._db, operations)
        self.relationships = Relationships(self._db, operations)

    def transaction(self):
        """Allows usage of the with-statement for Neo4j transactions::

          with graphdb.transaction:
              doMutatingOperations()
        """
        tx = self._db.beginTx()
        try:
            yield tx
            tx.success()
        finally:
            tx.finish()
    transaction = contextmanager(transaction)

    def node(self, **properties):
        node = self._db.createNode()
        for key, val in properties.items():
            node[key] = val
        return Node(node)

    def close(self):
        self._db.shutdown()
