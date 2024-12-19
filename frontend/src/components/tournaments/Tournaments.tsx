import { useEffect, useState } from "react";
import { apiClient } from "@/api/client";
import { Link, useNavigate } from "react-router-dom";
import { Plus, Users, Calendar } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import type { Tournament } from "@/types";

export const Tournaments = () => {
    const { user } = useAuth();
    const navigate = useNavigate();

    const [tournaments, setTournaments] = useState<Tournament[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchTournaments = async () => {
            try {
                const { data } = await apiClient.get("/tournaments");
                setTournaments(data);
                setIsLoading(false);
            } catch (error) {
                setError("Ошибка при загрузке турниров");
                setIsLoading(false);
            }
        };

        fetchTournaments();
    }, []);

    if (isLoading) {
        return <div>Загрузка турниров...</div>;
    }

    if (error) {
        return <div>Ошибка: {error}</div>;
    }

    return (
        <div className="container mx-auto py-6">
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Турниры</h1>
                    <p className="text-muted-foreground">
                        Управление киберспортивными турнирами
                    </p>
                </div>
                {user?.role === "ADMIN" && (
                    <Button
                        onClick={() => navigate("/tournaments/create")}
                        className="flex items-center gap-2"
                        variant="default"
                    >
                        <Plus className="w-4 h-4" />
                        Создать турнир
                    </Button>
                )}
            </div>

            {tournaments.length === 0 ? (
                <p>Нет доступных турниров</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {tournaments.map((tournament) => (
                        <div
                            key={tournament.id}
                            className="bg-card rounded-lg border border-border p-6 hover:border-primary/50 transition-colors"
                        >
                            <div className="mb-4">
                                <h3 className="text-xl font-semibold">
                                    {tournament.name}
                                </h3>
                                <p className="text-muted-foreground text-sm">
                                    {tournament.type}
                                </p>
                            </div>
                            <div className="space-y-4">
                                <div className="flex items-center gap-2 text-muted-foreground">
                                    <Users className="h-4 w-4" />
                                    <span>
                                        {tournament.registered_teams}/
                                        {tournament.max_teams} команд
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-muted-foreground">
                                    <Calendar className="h-4 w-4" />
                                    <span>
                                        {new Date(
                                            tournament.start_date
                                        ).toLocaleDateString()}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center mt-4">
                                    <span className="text-sm font-medium text-primary">
                                        {tournament.status}
                                    </span>
                                    <Link to={`/tournaments/${tournament.id}`}>
                                        <Button variant="secondary" size="sm">
                                            Подробнее
                                        </Button>
                                    </Link>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
