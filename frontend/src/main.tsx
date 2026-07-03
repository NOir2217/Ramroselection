  import { createRoot } from "react-dom/client";
  import { BrowserRouter } from "react-router";
  import App from "./app/App.tsx";
  import "./styles/index.css";
  import { AuthProvider } from "./app/context/AuthContext.tsx";
  import { CompareProvider } from "./app/context/CompareContext.tsx";

  createRoot(document.getElementById("root")!).render(
    <BrowserRouter>
      <AuthProvider>
        <CompareProvider>
          <App />
        </CompareProvider>
      </AuthProvider>
    </BrowserRouter>
  );