import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

export const TournamentBracket = ({
    tournamentId,
}: {
    tournamentId: number;
}) => {
    const { data: bracket, isLoading } = useQuery({
        queryKey: ["tournament", tournamentId, "bracket"],
        queryFn: async () => {
            const { data } = await apiClient.get(
                `/tournaments/${tournamentId}/bracket`
            );
            return data;
        },
    });

    if (isLoading) return <div>Загрузка...</div>;

    return (
        <div className="tournament-bracket">
            {bracket.rounds.map((round, roundIndex) => (
                <div key={roundIndex} className="round">
                    {round.matches.map((match, matchIndex) => (
                        <div key={matchIndex} className="match">
                            <div className="team">
                                {match.team1?.name || "TBD"}
                            </div>
                            <div className="team">
                                {match.team2?.name || "TBD"}
                            </div>
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
};
