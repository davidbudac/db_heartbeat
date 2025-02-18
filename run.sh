# Compile
javac --release 8 -cp ".:oraclepki.jar:osdt_core.jar:osdt_cert.jar:ojdbc8.jar" OracleDBConnect.java 

# Create JAR with all dependencies
jar cvfm OracleDBConnect.jar manifest.txt *.class ojdbc8.jar oraclepki.jar osdt_core.jar osdt_cert.jar

# Run
java -jar OracleDBConnect.jar


# path to jars:  /mnt/c/app/client/david/product/19.0.0/client_1/jlib/