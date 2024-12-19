import { useAuth } from "@/contexts/AuthContext";
import { useEffect } from "react";

const ProtectedPage = () => {
    const { user, loading } = useAuth();

    useEffect(() => {
        if (!loading && !user) {
            // Можно добавить дополнительную логику, если требуется
        }
    }, [loading, user]);

    if (loading) {
        return <div>Загрузка...</div>;
    }

    if (!user) {
        return (
            <div style={{ color: "red" }}>
                Не удалось загрузить данные пользователя.
            </div>
        );
    }

    return <div>Welcome, {user.username}!</div>;
};

export default ProtectedPage;
