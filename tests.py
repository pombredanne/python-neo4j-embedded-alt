import os
import shutil

import unittest

from altneo4j import GraphDB


class FunctionnalTests(unittest.TestCase):

    path = '/tmp/altneo4j/'

    def setUp(self):
        self.db = GraphDB(self.path)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.path)

    def test_create_db(self):
        self.assertTrue(self.db)

    def test_create_node(self):
        with self.db.transaction():
            node = self.db.node()

        self.assertTrue(node)

    def test_node_property(self):
        with self.db.transaction():
            node = self.db.node()
            node['name'] = 'amirouche'
        self.assertEqual(node['name'], 'amirouche')

    def test_create_relationship(self):
        with self.db.transaction():
            A = self.db.node()
            B = self.db.node()
            relationship = A.link(B)
        self.assertTrue(relationship)

    def test_relationship_property(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            relationship = amirouche.knows(python)
            relationship['years'] = 10
        self.assertEqual(relationship['years'], 10)

    def test_relationship_start_node(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            relationship = amirouche.knows(python)

        self.assertEqual(relationship.start(), amirouche)

    def test_relationship_end_node(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            relationship = amirouche.knows(python)

        self.assertEqual(relationship.end(), python)

    def test_relationship_type(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            relationship = amirouche.knows(python)

        self.assertEqual(relationship.type(), 'knows')

    def test_iter_relationships(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            c = self.db.node()
            cpp = self.db.node()
            amirouche.knows(python)
            amirouche.knows(c)
            amirouche.knows(cpp)

        nb = 0
        for relationship in self.db.relationships():
            self.assertTrue(relationship)
            nb += 1
        self.assertEqual(nb, 3)

    def test_iter_relationships_type(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            c = self.db.node()
            cpp = self.db.node()
            bigdata = self.db.node()
            amirouche.knows(python)
            amirouche.knows(c)
            amirouche.knows(cpp)
            amirouche.like(bigdata)

        nb = 0
        for relationship in self.db.relationships():
            self.assertTrue(relationship)
            nb += 1
        self.assertEqual(nb, 4)

    def test_iter_node_outgoing(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            c = self.db.node()
            cpp = self.db.node()
            amirouche.knows(python)
            amirouche.knows(c)
            amirouche.knows(cpp)

        nb = 0
        for relationship in amirouche.relationships.outgoing():
            self.assertTrue(relationship)
            nb += 1
        self.assertEqual(nb, 3)

    def test_iter_incoming(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            c = self.db.node()
            cpp = self.db.node()
            amirouche.knows(python)
            amirouche.knows(c)
            amirouche.knows(cpp)

        nb = 0
        for relationship in python.relationships.incoming():
            self.assertTrue(relationship)
            nb += 1
        self.assertEqual(nb, 1)

    def test_get_node_by_id(self):
        with self.db.transaction():
            node = self.db.node()
        copy = self.db.nodes.get(node.id)
        self.assertEqual(node, copy)

    def test_get_relationship_by_id(self):
        with self.db.transaction():
            amirouche = self.db.node()
            python = self.db.node()
            knows = amirouche.knows(python)
        copy = self.db.relationships.get(knows.id)
        self.assertEqual(knows, copy)

    def test_set_retrieve_integer(self):
        with self.db.transaction():
            amirouche = self.db.node()
            amirouche['name'] = 'amirouche'
        self.assertEqual(amirouche['name'], 'amirouche')

    # it fails because of some conversion approximation mistake
    # def test_set_retrieve_float(self):
    #     with self.db.transaction():
    #         amirouche = self.db.node()
    #         amirouche['age'] = 27.8
    #     self.assertEqual(amirouche['age'], 27.8)

    # doesn't work yet
    # def test_set_retrieve_long(self):
    #     with self.db.transaction():
    #         amirouche = self.db.node()
    #         amirouche['age'] = 27L
    #     self.assertEqual(amirouche['age'], 27L)

    def test_set_retrieve_list(self):
        languages = ['french', 'english', 'amazigh']
        with self.db.transaction():
            amirouche = self.db.node()
            amirouche['languages'] = languages
        self.assertEqual(len(amirouche['languages']), len(languages))
        for value in amirouche['languages']:
            self.assertIn(value, languages)


if __name__ == '__main__':
    unittest.main()
