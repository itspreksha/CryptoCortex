import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import BackButton from "../components/BackButton";
import styles from "../styles/Auth.module.css";

const Register = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      const response = await axios.post(
        "https://cryptocortex-1.onrender.com/register",
        {
          username,
          password,
        }
      );
      setMessage(response.data.message || "Registration completed.");

      // Redirect on HTTP success status
      if (response.status >= 200 && response.status < 300) {
        // give user a short moment to read the message, then navigate
        setTimeout(() => navigate("/login"), 600);
      }
    } catch (error) {
      console.error("Registration failed:", error);
      setMessage(error.response?.data?.detail || "Registration error");
    }
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authTop}>
        <BackButton />
      </div>

      <div className={styles.authContainer}>
        <div className={styles.authBox}>
          <h2>Register</h2>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button className={styles.authButton} onClick={handleRegister}>
            Register
          </button>
          {message && <p className={styles.authMessage}>{message}</p>}
          <p className={styles.authLink}>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
