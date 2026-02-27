import { useState } from "react";
import { api } from "../api";
import { setAuth } from "../store";

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    if (isRegister) {
      // Registration
      if (password !== confirmPassword) {
        setError("Passwords do not match");
        setLoading(false);
        return;
      }
      if (password.length < 3) {
        setError("Password must be at least 3 characters");
        setLoading(false);
        return;
      }
      try {
        await api.post("/auth/register", { username, password });
        setSuccess("Account created! You can now sign in.");
        setIsRegister(false);
        setPassword("");
        setConfirmPassword("");
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Registration failed");
      } finally {
        setLoading(false);
      }
    } else {
      // Login
      try {
        const { data } = await api.post("/auth/login", { username, password });
        setAuth({ token: data.token, username: data.username });
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Login failed");
      } finally {
        setLoading(false);
      }
    }
  }

  function toggleMode() {
    setIsRegister(!isRegister);
    setError(null);
    setSuccess(null);
    setPassword("");
    setConfirmPassword("");
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>FARAGNY</h1>
        <p className="subtitle">
          {isRegister ? "Create your account" : "Discover movies you'll love"}
        </p>
        
        <form className="login-form" onSubmit={onSubmit}>
          <div className="input-group">
            <input
              type="text"
              id="username"
              placeholder=" "
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
            <label htmlFor="username">Username</label>
          </div>
          
          <div className="input-group">
            <input
              type="password"
              id="password"
              placeholder=" "
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isRegister ? "new-password" : "current-password"}
            />
            <label htmlFor="password">Password</label>
          </div>

          {isRegister && (
            <div className="input-group">
              <input
                type="password"
                id="confirmPassword"
                placeholder=" "
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
              />
              <label htmlFor="confirmPassword">Confirm Password</label>
            </div>
          )}
          
          {error && <div className="login-error">{error}</div>}
          {success && <div className="login-success">{success}</div>}
          
          <button type="submit" className="login-btn" disabled={loading}>
            {loading
              ? (isRegister ? "Creating account..." : "Signing in...")
              : (isRegister ? "Create Account" : "Sign In")}
          </button>
        </form>
        
        <div className="login-footer">
          {isRegister ? (
            <>
              Already have an account?{" "}
              <button className="link-btn" onClick={toggleMode}>
                Sign In
              </button>
            </>
          ) : (
            <>
              New to Faragny?{" "}
              <button className="link-btn" onClick={toggleMode}>
                Create an account
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
