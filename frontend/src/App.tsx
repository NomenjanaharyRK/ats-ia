import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { RequireAuth } from "./auth/RequireAuth";
import LoginPage from "./pages/Login";
import OffersList from "./pages/OffersList";
import OfferScoring from "./pages/OfferScoring";
import NewOfferPage from "./pages/NewOfferPage";
import NewApplicationPage from "./pages/NewApplicationPage";


const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<RequireAuth />}>
            <Route path="/offers" element={<OffersList />} />
            <Route path="/offers/new" element={<NewOfferPage />} />
            <Route path="/offers/:offerId" element={<OfferScoring />} />
            <Route
              path="/offers/:offerId/apply"
              element={<NewApplicationPage />}
            />
          </Route>

          <Route path="*" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
