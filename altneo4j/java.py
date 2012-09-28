import os
import sys

from pkg_resources import resource_filename


class_path = resource_filename(__name__, 'javalib')


divider = ';' if sys.platform == "win32" else ':'
os.environ['CLASSPATH'] = '%s%s%s/*' % (
    os.environ['CLASSPATH'],
    divider,
    class_path
)


from jnius import autoclass


NEO4J_JAVA_CLASSES = (
    'org.neo4j.graphdb.Direction',
    'org.neo4j.kernel.EmbeddedGraphDatabase',
    'org.neo4j.tooling.GlobalGraphOperations',
    'org.neo4j.graphdb.DynamicRelationshipType',
    'java.util.HashMap',
)


for class_path in NEO4J_JAVA_CLASSES:
    class_name = class_path.split('.')[-1]
    klass = autoclass(class_path)
    globals()[class_name] = klass
