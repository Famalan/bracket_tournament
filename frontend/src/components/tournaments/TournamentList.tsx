import { useQuery } from "@tanstack/react-query";
import { Tournament } from "@/types";
import { TournamentCard } from "./TournamentCard";
import { tournamentService } from "@/services/tournamentService";

export function TournamentList() {
    const { data: tournaments = [], isLoading } = useQuery({
        queryKey: ["tournaments"],
        queryFn: tournamentService.getAll,
    });

    if (isLoading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                    <div
                        key={i}
                        className="h-48 rounded-lg bg-muted animate-pulse"
                    />
                ))}
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tournaments.map((tournament: Tournament) => (
                <TournamentCard key={tournament.id} tournament={tournament} />
            ))}
        </div>
    );
}