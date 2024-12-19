import { Route, Routes as RouterRoutes } from "react-router-dom";
import { Login } from "../pages/Login";
import { PrivateRoute } from "./PrivateRoute";
import { Home } from "../pages/Home";
import Tournaments from "../pages/Tournaments";
import TournamentDetails from "../pages/TournamentDetails";
import EditTournament from "../pages/EditTournament";
import { CreateTournament } from "@/pages/CreateTournament";

export function Routes() {
    return (
        <RouterRoutes>
            <Route path="/login" element={<Login />} />
            <Route
                path="/"
                element={
                    <PrivateRoute>
                        <Home />
                    </PrivateRoute>
                }
            />
            <Route
                path="/tournaments"
                element={
                    <PrivateRoute>
                        <Tournaments />
                    </PrivateRoute>
                }
            />
            <Route
                path="/tournaments/:id"
                element={
                    <PrivateRoute>
                        <TournamentDetails />
                    </PrivateRoute>
                }
            />
            <Route
                path="/tournaments/create"
                element={
                    <ProtectedRoute allowedRoles={["admin"]}>
                        <CreateTournament />
                    </ProtectedRoute>
                }
            />
        </RouterRoutes>
    );
}
