if "%ORACLE_HOME%"=="" set ORACLE_HOME=c:\app\client\david\product\19.0.0\client_1

cp %ORACLE_HOME%\jdbc\lib\ojdbc8.jar .\lib
cp %ORACLE_HOME%\jlib\oraclepki.jar .\lib
cp %ORACLE_HOME%\jlib\osdt_core.jar .\lib
cp %ORACLE_HOME%\jlib\osdt_cert.jar .\lib

%ORACLE_HOME%\jdk\bin\javac.exe -cp ".;.\lib\oraclepki.jar;.\lib\osdt_core.jar;.\lib\osdt_cert.jar;.\lib\ojdbc8.jar" OracleDBConnect.java 
%ORACLE_HOME%\jdk\bin\jar.exe cvfm OracleDBConnect.jar manifest.txt *.class .\jdbc\ojdbc8.jar .\lib\oraclepki.jar .\lib\osdt_core.jar .\lib\osdt_cert.jar
%ORACLE_HOME%\jdk\bin\java.exe -cp ".;.\lib\oraclepki.jar;.\lib\osdt_core.jar;.\lib\osdt_cert.jar;.\jdbc\lib\ojdbc8.jar"  -jar OracleDBConnect.jar
