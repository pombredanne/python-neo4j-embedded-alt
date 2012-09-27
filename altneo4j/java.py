import os
import sys
import inspect
from pkg_resources import resource_listdir
from pkg_resources import resource_filename

import jpype




# build jvmargs
jars = []
for name in resource_listdir(__name__, 'javalib'):
    if name.endswith('.jar'):
        jars.append(resource_filename(__name__, "javalib/%s" % name))
if len(jars) > 0:
    divider = ';' if sys.platform == "win32" else ':'
    classpath = divider.join(jars)

jvm_args = ['-Djava.class.path=%s' % classpath]

if os.getenv('DEBUG', None) == 'true':
    jvm_args.append('-Xdebug')
    jvm_args.append('-Xnoagent')
    jvm_args.append('-Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8000')


# run jvm
jpype.startJVM(jpype.getDefaultJVMPath(), *jvm_args)

NEO4J_JAVA_CLASSES = (
    'org.neo4j.graphdb.Direction',
    'org.neo4j.kernel.EmbeddedGraphDatabase',
    'org.neo4j.tooling.GlobalGraphOperations',
    'org.neo4j.graphdb.DynamicRelationshipType',
    'java.util.HashMap',
)


for class_path in NEO4J_JAVA_CLASSES:
    class_path = class_path.split('.')
    package, class_name = '.'.join(class_path[:-1]), class_path[-1]
    package = jpype.JPackage(package)
    klass = getattr(package, class_name)
    globals()[class_name] = klass
