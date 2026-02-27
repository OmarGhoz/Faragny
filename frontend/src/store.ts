import { setAuthToken } from "./api";

export type AuthState = {
  token: string | null;
  username: string | null;
};

// Always start logged out - require fresh login each session
let authState: AuthState = {
  token: null,
  username: null,
};

const subscribers = new Set<() => void>();

export function getAuth(): AuthState {
  return authState;
}

export function setAuth(next: AuthState) {
  authState = next;
  if (next.token) {
    localStorage.setItem("token", next.token);
    setAuthToken(next.token);
  } else {
    localStorage.removeItem("token");
    setAuthToken(null);
  }
  if (next.username) localStorage.setItem("username", next.username);
  else localStorage.removeItem("username");
  subscribers.forEach((fn) => fn());
}

export function subscribe(fn: () => void) {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
}


