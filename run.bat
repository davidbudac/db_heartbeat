set ORACLE_HOME=c:\app\client\david\product\19.0.0\client_1

rem Compile
%ORACLE_HOME%\jdk\bin\javac.exe -cp ".;%ORACLE_HOME%\jlib\oraclepki.jar;%ORACLE_HOME%\jlib\osdt_core.jar;%ORACLE_HOME%\jlib\osdt_cert.jar;%ORACLE_HOME%\jdbc\lib\ojdbc8.jar" OracleDBConnect.java 

# Create JAR with all dependencies
%ORACLE_HOME%\jdk\bin\jar cvfm OracleDBConnect.jar manifest.txt *.class ojdbc8.jar oraclepki.jar osdt_core.jar osdt_cert.jar

# Run
%ORACLE_HOME%\jdk\bin\java -jar OracleDBConnect.jar
