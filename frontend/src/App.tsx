import { useEffect, useSyncExternalStore } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import { getAuth, setAuth, subscribe } from "./store";
import { setAuthToken } from "./api";
import Login from "./pages/Login";
import Catalog from "./pages/Catalog";

function useAuth() {
  return useSyncExternalStore(subscribe, getAuth, getAuth);
}

function AuthedApp() {
  const navigate = useNavigate();
  const auth = useAuth();

  useEffect(() => {
    setAuthToken(auth.token);
  }, [auth.token]);

  if (!auth.token) {
    return <Login />;
  }

  return (
    <Routes>
      <Route path="/" element={<Catalog />} />
    </Routes>
  );
}

export default function App() {
  return <AuthedApp />;
}
