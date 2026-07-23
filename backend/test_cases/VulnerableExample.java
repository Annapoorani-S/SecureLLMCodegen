package test;

import java.sql.*;

public class VulnerableExample {

    public void login(String username) throws Exception {

        Connection con = DriverManager.getConnection(
            "jdbc:postgresql://localhost/bank",
            "admin",
            "password"
        );

        String query =
            "SELECT * FROM users WHERE username='" 
            + username + "'";

        Statement stmt = con.createStatement();

        ResultSet rs = stmt.executeQuery(query);
    }
}