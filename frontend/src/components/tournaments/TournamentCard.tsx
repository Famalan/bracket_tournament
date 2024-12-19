import { Tournament } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Calendar, Users } from "lucide-react";

interface TournamentCardProps {
    tournament: Tournament;
}

export function TournamentCard({ tournament }: TournamentCardProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>{tournament.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        <span>
                            {tournament.registeredTeams} / {tournament.maxTeams}{" "}
                            команд
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>
                            {new Date(tournament.startDate).toLocaleDateString()}
                        </span>
                    </div>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-primary">
                        {tournament.status}
                    </span>
                    <Button asChild variant="secondary" size="sm">
                        <Link to={`/tournaments/${tournament.id}`}>
                            Подробнее
                        </Link>
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}