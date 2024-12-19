import React from "react";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Home } from "@/pages/Home";
import { Teams } from "@/pages/Teams";
import { Schedule } from "@/pages/Schedule";
import { Settings } from "@/pages/Settings";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { RegisterPage } from "@/features/auth/pages/RegisterPage";
import Tournaments from "./pages/Tournaments";
import { DashboardLayout } from "@/components/DashboardLayout";
import { CreateTournament } from "@/pages/CreateTournament";
import { AdminRoute } from "@/components/auth/AdminRoute";
import { EditTournament } from "@/pages/EditTournament";
import { Users } from "@/pages/Users";
import { TournamentDetails } from "@/pages/TournamentDetails";

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    return children;
};

function App() {
    return (
        <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route
                element={
                    <PrivateRoute>
                        <DashboardLayout>
                            <Outlet />
                        </DashboardLayout>
                    </PrivateRoute>
                }
            >
                <Route path="/" element={<Home />} />
                <Route path="/teams" element={<Teams />} />
                {/* <Route path="/schedule" element={<Schedule />} />
                <Route path="/settings" element={<Settings />} /> */}
                <Route path="/tournaments" element={<Tournaments />} />
                <Route
                    path="/tournaments/create"
                    element={
                        <AdminRoute>
                            <CreateTournament />
                        </AdminRoute>
                    }
                />
                <Route
                    path="/tournaments/:id"
                    element={<TournamentDetails />}
                />
                <Route
                    path="/tournaments/:id/edit"
                    element={
                        <AdminRoute>
                            <EditTournament />
                        </AdminRoute>
                    }
                />
                <Route
                    path="/users"
                    element={
                        <AdminRoute>
                            <Users />
                        </AdminRoute>
                    }
                />
            </Route>
        </Routes>
    );
}

export default App;
