import { useNavigate, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Plus, Edit, Trash2 } from "lucide-react";
import { api } from "@/lib/api";

export default function Tournaments() {
    const navigate = useNavigate();
    const { user, isAdmin } = useAuth();

    const { data: tournaments = [], isLoading } = useQuery({
        queryKey: ["tournaments"],
        queryFn: async () => {
            const { data } = await api.get("/tournaments");
            return data;
        },
    });

    const handleDelete = async (id: number) => {
        if (window.confirm("Вы уверены, что хотите удалить этот турнир?")) {
            try {
                await api.delete(`/tournaments/${id}`);
                window.location.reload();
            } catch (error) {
                console.error("Ошибка при удалении турнира:", error);
            }
        }
    };

    if (isLoading) {
        return <div>Загрузка...</div>;
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
                {isAdmin && (
                    <Button
                        onClick={() => navigate("/tournaments/create")}
                        className="flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Создать турнир
                    </Button>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {tournaments.map((tournament: any) => (
                    <div
                        key={tournament.id}
                        className="bg-card rounded-lg border p-6 space-y-4"
                    >
                        <div>
                            <h3 className="text-xl font-semibold">
                                {tournament.name}
                            </h3>
                            <p className="text-muted-foreground text-sm">
                                {tournament.type}
                            </p>
                        </div>

                        <div className="flex justify-between items-center">
                            <Button
                                variant="secondary"
                                onClick={() =>
                                    navigate(`/tournaments/${tournament.id}`)
                                }
                            >
                                Подробнее
                            </Button>

                            {isAdmin && (
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="icon"
                                        onClick={() =>
                                            navigate(
                                                `/tournaments/${tournament.id}/edit`
                                            )
                                        }
                                    >
                                        <Edit className="w-4 h-4" />
                                    </Button>
                                    <Button
                                        variant="destructive"
                                        size="icon"
                                        onClick={() =>
                                            handleDelete(tournament.id)
                                        }
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
