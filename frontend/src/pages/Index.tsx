import { Plus, Users, Calendar } from "lucide-react";
import { Link } from "react-router-dom";
import { DashboardLayout } from "@/components/DashboardLayout";

const Index = () => {
    const tournaments = [
        {
            id: 1,
            name: "CS:GO Summer Championship",
            type: "Double Elimination",
            teams: 16,
            startDate: "2024-06-15",
            status: "Регистрация",
        },
        {
            id: 2,
            name: "Dota 2 Pro League",
            type: "Single Elimination",
            teams: 8,
            startDate: "2024-07-01",
            status: "Скоро",
        },
    ];

    return (
        <DashboardLayout>
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Турниры</h1>
                    <p className="text-muted-foreground">
                        Управление киберспортивными турнирами
                    </p>
                </div>
                <Link to="/tournaments/create">
                    <button className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors">
                        <Plus className="mr-2 h-4 w-4" /> Создать турнир
                    </button>
                </Link>
            </div>

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
                                <span>{tournament.teams} команд</span>
                            </div>
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Calendar className="h-4 w-4" />
                                <span>{tournament.startDate}</span>
                            </div>
                            <div className="flex justify-between items-center mt-4">
                                <span className="text-sm font-medium text-primary">
                                    {tournament.status}
                                </span>
                                <button className="px-3 py-1 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80 transition-colors text-sm">
                                    Подробнее
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </DashboardLayout>
    );
};

export default Index;
