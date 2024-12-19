import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

export function AdminRoute({ children }: { children: React.ReactNode }) {
    const { user, isAuthenticated, isLoading, isAdmin } = useAuth();

    console.log("AdminRoute check:", {
        isAuthenticated,
        isAdmin,
        userRole: user?.role,
    });

    if (isLoading) {
        return <div>Загрузка...</div>;
    }

    if (!isAuthenticated || !isAdmin) {
        return <Navigate to="/tournaments" replace />;
    }

    return <>{children}</>;
}
