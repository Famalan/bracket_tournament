import { CreateTournamentForm } from "@/components/tournaments/CreateTournamentForm";
import { useAuth } from "@/hooks/useAuth";

export function CreateTournament() {
    const { isAdmin } = useAuth();

    return (
        <div className="container mx-auto py-6">
            <div className="mb-8">
                <h1 className="text-3xl font-bold">Создание турнира</h1>
                <p className="text-muted-foreground">
                    Заполните форму для создания нового турнира
                </p>
            </div>
            <div className="max-w-2xl">
                <CreateTournamentForm />
            </div>
        </div>
    );
}
