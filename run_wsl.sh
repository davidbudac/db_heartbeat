export ORACLE_HOME=/mnt/c/app/client/david/product/19.0.0/client_1

cp $ORACLE_HOME/jdbc/lib/ojdbc8.jar ./lib
cp $ORACLE_HOME/jlib/oraclepki.jar ./lib
cp $ORACLE_HOME/jlib/osdt_core.jar ./lib
cp $ORACLE_HOME/jlib/osdt_cert.jar ./lib

# Compile
$ORACLE_HOME/jdk/bin/javac.exe -cp ".;./lib/oraclepki.jar;./lib/osdt_core.jar;./lib/osdt_cert.jar;./lib/ojdbc8.jar" ./OracleDBConnect.java 

# Create JAR with all dependencies
$ORACLE_HOME/jdk/bin/jar.exe cvfm OracleDBConnect.jar manifest.txt *.class ./lib/ojdbc8.jar ./lib/oraclepki.jar ./lib/osdt_core.jar ./lib/osdt_cert.jar

# Run
$ORACLE_HOME/jdk/bin/java.exe -jar OracleDBConnect.jar
