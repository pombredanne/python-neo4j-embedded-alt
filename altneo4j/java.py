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
from jnius.reflect import Object


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


def to_java(value):
    if isinstance(value, Object):
        return value
    elif isinstance(value, (str, unicode)):
        String = autoclass('java.lang.String')
        return String(value)
    elif isinstance(value, int):
        Integer = autoclass('java.lang.Integer')
        return Integer(value)
    elif isinstance(value, float):
        Float = autoclass('java.lang.Float')
        return Float(value)
    # elif isinstance(value, long):
    #     Long = autoclass('java.lang.Long')
    #     return Long(value)
    elif isinstance(value, list):
        ArrayList = autoclass('java.util.ArrayList')
        out = ArrayList
        for v in value:
            out.add(to_java(v))
        return out
    elif isinstance(value, dict):
        map = HashMap()
        for k, v in value.iteritems():
            map.put(k, to_java(v))
        return map
    else:
        import debug
        raise TypeError('type not supported')


def from_java(value):
    if isinstance(value, autoclass('java.lang.Integer')):
        return value.intValue()
    # if isinstance(value, autoclass('java.lang.Long')):
    #     return value.longValue()
    if isinstance(value, autoclass('java.lang.Float')):
        return value.floatValue()
    if isinstance(value, autoclass('java.util.ArrayList')):
        out = []
        iterator = value.iterator()
        while iterator.hasNext():
            out.append(from_java(iterator.next()))
        return out
    return value
