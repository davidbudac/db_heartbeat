export ORACLE_HOME=/mnt/c/app/client/david/product/19.0.0/client_1

# Compile
$ORACLE_HOME/jdk/bin/javac.exe --release 8 -cp ".:$ORACLE_HOME/jlib/oraclepki.jar:$ORACLE_HOME/jlib/osdt_core.jar:$ORACLE_HOME/jlib/osdt_cert.jar:$ORACLE_HOME/jlib/ojdbc8.jar" OracleDBConnect.java 

# Create JAR with all dependencies
$ORACLE_HOME/jdk/bin/jar cvfm OracleDBConnect.jar manifest.txt *.class ojdbc8.jar oraclepki.jar osdt_core.jar osdt_cert.jar

# Run
$ORACLE_HOME/jdk/bin/java -jar OracleDBConnect.jar


# path to jars:  /mnt/c/app/client/david/product/19.0.0/client_1/jlib/ , /mnt/c/app/client/david/product/19.0.0/client_1/jdbc/lib/ojdbc8.jar

# scp db@192.168.178.70:/mnt/c/app/client/david/product/19.0.0/client_1/jdbc/lib/ojdbc8.jar ./
# scp db@192.168.178.70:/mnt/c/app/client/david/product/19.0.0/client_1/jlib/oraclepki.jar ./
# scp db@192.168.178.70:/mnt/c/app/client/david/product/19.0.0/client_1/jlib/osdt_core.jar ./
# scp db@192.168.178.70:/mnt/c/app/client/david/product/19.0.0/client_1/jlib/osdt_cert.jar ./