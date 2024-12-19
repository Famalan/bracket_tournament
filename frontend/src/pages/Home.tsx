import { Link } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Plus } from "lucide-react";

export const Home = () => {
    const { user } = useAuth();

    return (
        <div className="flex flex-col items-center justify-center space-y-6 text-center">
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl">
                Добро пожаловать в мир киберспортивных турниров
            </h1>
            <p className="max-w-[600px] text-muted-foreground">
                Организуйте турниры, создавайте команды и участвуйте в
                соревнованиях. Наша платформа предоставляет все необходимые
                инструменты для проведения киберспортивных мероприятий любого
                масштаба.
            </p>
            <div className="flex gap-4">
                <Link
                    to="/tournaments"
                    className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90"
                >
                    Просмотреть турниры
                </Link>
                {user?.role === "ADMIN" && (
                    <Link
                        to="/tournaments/create"
                        className="inline-flex h-10 items-center justify-center rounded-md bg-secondary px-8 text-sm font-medium text-secondary-foreground shadow transition-colors hover:bg-secondary/90"
                    >
                        <Plus className="mr-2 h-4 w-4" />
                        Создать турнир
                    </Link>
                )}
            </div>
        </div>
    );
};
