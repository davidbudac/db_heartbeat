import oracle.jdbc.OracleDriver;
import java.io.FileInputStream;
import java.util.Properties;
import java.util.HashSet;
import java.util.Set;
import java.sql.*;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.logging.*;
import java.util.ArrayList;
import java.util.List;


public class OracleDBConnect {

    private static final Logger LOGGER = Logger.getLogger(OracleDBConnect.class.getName());
    private static final Logger CSV_LOGGER = Logger.getLogger("CSVLogger");
    private static Properties sqlProps;  // Add this field

    private static class DatabaseWorker implements Runnable {
        private final String dbName;
        private final String dbUrl;
        private final String dbUsername;
        private final String dbPassword;
        private final long interval;

        public DatabaseWorker(String dbName, String dbUrl, String dbUsername, String dbPassword, long interval) {
            this.dbName = dbName;
            this.dbUrl = dbUrl;
            this.dbUsername = dbUsername;
            this.dbPassword = dbPassword;
            this.interval = interval;
        }

        @Override
        public void run() {
            LOGGER.info("Starting test cycle for database: " + dbName);
            
            // Run all iterations for this database
            for (int i = 0; i < 10; i++) {
                Connection conn = null;
                Statement stmt = null;
                ResultSet rs = null;
                long lastOperationTime = 0;

                try {
                    // Connect for each query
                    long connectStartTime = System.currentTimeMillis();
                    conn = establishConnection(dbUrl, dbUsername, dbPassword);
                    conn.setAutoCommit(false);
                    long connectDuration = System.currentTimeMillis() - connectStartTime;
                    logOperation(dbName, "connect", connectDuration, 0);
                    lastOperationTime = connectStartTime;

                    // First operation - SELECT
                    stmt = conn.createStatement();
                    long selectStartTime = System.currentTimeMillis();
                    rs = stmt.executeQuery(sqlProps.getProperty("sql.select"));
                    if (rs.next()) {
                        long selectDuration = System.currentTimeMillis() - selectStartTime;
                        logOperation(dbName, "select", selectDuration, selectStartTime - lastOperationTime);
                        lastOperationTime = selectStartTime;
                    }

                    // Second operation - INSERT
                    long insertStartTime = System.currentTimeMillis();
                    stmt.executeUpdate(sqlProps.getProperty("sql.insert"));
                    long insertDuration = System.currentTimeMillis() - insertStartTime;
                    logOperation(dbName, "insert", insertDuration, insertStartTime - lastOperationTime);
                    lastOperationTime = insertStartTime;

                    // Third operation - UPDATE
                    long updateStartTime = System.currentTimeMillis();
                    stmt.executeUpdate(sqlProps.getProperty("sql.update"));
                    long updateDuration = System.currentTimeMillis() - updateStartTime;
                    logOperation(dbName, "update", updateDuration, updateStartTime - lastOperationTime);
                    lastOperationTime = updateStartTime;

                    // Fourth operation - DELETE
                    long deleteStartTime = System.currentTimeMillis();
                    stmt.executeUpdate(sqlProps.getProperty("sql.delete"));
                    long deleteDuration = System.currentTimeMillis() - deleteStartTime;
                    logOperation(dbName, "delete", deleteDuration, deleteStartTime - lastOperationTime);
                    lastOperationTime = deleteStartTime;

                    // Fifth operation - COMMIT
                    long commitStartTime = System.currentTimeMillis();
                    conn.commit();
                    long commitDuration = System.currentTimeMillis() - commitStartTime;
                    logOperation(dbName, "commit", commitDuration, commitStartTime - lastOperationTime);

                    // Log iteration completion
                    LOGGER.log(Level.FINE, String.format("Database %s completed iteration %d of 10", dbName, i + 1));

                } catch (SQLException e) {
                    LOGGER.log(Level.SEVERE, "Database error: " + e.getMessage(), e);
                    e.printStackTrace();
                } finally {
                    // Close resources
                    try {
                        if (rs != null) rs.close();
                        if (stmt != null) stmt.close();
                        if (conn != null) conn.close();
                    } catch (SQLException e) {
                        LOGGER.log(Level.SEVERE, "Error closing resources", e);
                    }
                }

                // Wait for configured interval before next iteration (except for the last iteration)
                if (i < 9) {
                    try {
                        Thread.sleep(interval);
                    } catch (InterruptedException e) {
                        LOGGER.log(Level.SEVERE, "Sleep interrupted", e);
                        Thread.currentThread().interrupt();
                    }
                }
            }
            
            LOGGER.info("Completed test cycle for database: " + dbName);
        }
    }

    public static void main(String[] args) {
        configureLogging();
        CSV_LOGGER.info("database,operation,timestamp,duration_ms,time_between_ms");

        try {
            // Load SQL statements
            sqlProps = new Properties();
            sqlProps.load(new FileInputStream("sql.properties"));

            // Load database configurations
            Properties dbProps = new Properties();
            dbProps.load(new FileInputStream("databases.properties"));

            // Get all unique database prefixes (db1, db2, etc.)
            Set<String> dbPrefixes = new HashSet<>();
            for (String key : dbProps.stringPropertyNames()) {
                dbPrefixes.add(key.substring(0, key.indexOf('.')));
            }

            // Create and start a thread for each database
            List<Thread> threads = new ArrayList<>();
            for (String prefix : dbPrefixes) {
                String dbName = dbProps.getProperty(prefix + ".name");
                String dbUrl = dbProps.getProperty(prefix + ".url");
                String dbUsername = dbProps.getProperty(prefix + ".username");
                String dbPassword = dbProps.getProperty(prefix + ".password");
                long interval = Long.parseLong(dbProps.getProperty(prefix + ".interval", "1000")); // Default to 1000ms

                Thread thread = new Thread(new DatabaseWorker(dbName, dbUrl, dbUsername, dbPassword, interval));
                threads.add(thread);
                thread.start();
            }

            // Wait for all threads to complete
            for (Thread thread : threads) {
                thread.join();
            }

        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error: " + e.getMessage(), e);
            e.printStackTrace();
        }
    }

    private static Connection establishConnection(String url, String username, String password) 
            throws SQLException {
        DriverManager.registerDriver(new OracleDriver());
        return DriverManager.getConnection(url, username, password);
    }

    private static void logOperation(String database, String operation, long duration, long delta) {
        LocalDateTime now = LocalDateTime.now();
        String timestamp = now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS"));
        CSV_LOGGER.info(String.format("%s,%s,%s,%d,%d", 
            database, operation, timestamp, duration, delta));
    }

    private static String formatTimestamp(Timestamp timestamp) {
        // Convert Timestamp to Instant
        Instant instant = timestamp.toInstant();

        // Convert Instant to LocalDateTime in your system's default time zone
        LocalDateTime localDateTime = LocalDateTime.ofInstant(instant, ZoneId.systemDefault());

        // Format LocalDateTime
        return localDateTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS"));
    }

    private static void configureLogging() {
        try {
            // Remove existing handlers
            Logger rootLogger = Logger.getLogger("");
            for (Handler handler : rootLogger.getHandlers()) {
                rootLogger.removeHandler(handler);
            }

            // Set logging level (FINE is equivalent to DEBUG in other logging frameworks)
            LOGGER.setLevel(Level.FINE);  // DEBUG equivalent
            Level debugLevel = Level.FINE; // For clarity

            // Configure standard logging with custom formatter
            FileHandler fileHandler = new FileHandler("oracle_db_connect.log", true);
            fileHandler.setLevel(debugLevel);
            fileHandler.setFormatter(new Formatter() {
                @Override
                public String format(LogRecord record) {
                    LocalDateTime timestamp = LocalDateTime.now();
                    String formattedTimestamp = timestamp.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS"));
                    // Replace "FINE" with "DEBUG" in the output
                    String level = record.getLevel().equals(Level.FINE) ? "DEBUG" : record.getLevel().getName();
                    return String.format("%s %s: %s%n", 
                        formattedTimestamp,
                        level,
                        record.getMessage());
                }
            });
            LOGGER.addHandler(fileHandler);
            
            // Configure CSV logging
            FileHandler csvHandler = new FileHandler("log.csv", true);
            csvHandler.setFormatter(new Formatter() {
                @Override
                public String format(LogRecord record) {
                    return record.getMessage() + System.lineSeparator();
                }
            });
            CSV_LOGGER.addHandler(csvHandler);
            
            // Add console handler with the same custom formatter
            ConsoleHandler consoleHandler = new ConsoleHandler();
            consoleHandler.setLevel(debugLevel);
            consoleHandler.setFormatter(fileHandler.getFormatter());
            LOGGER.addHandler(consoleHandler);

        } catch (Exception e) {
            System.err.println("Error configuring logger: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
