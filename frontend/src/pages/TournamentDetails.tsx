import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Trophy, Users } from "lucide-react";
import { toast } from "sonner";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";

// Добавим интерфейсы для типизации
interface Team {
    id: number;
    name: string;
    members?: { username: string }[];
}

interface Match {
    id: number;
    round: number;
    team1_id: number;
    team2_id: number;
    winner_id: number | null;
    status: string;
}

interface Tournament {
    id: number;
    name: string;
    description: string;
    status: string;
    type: string;
    teams?: Team[];
    matches?: Match[];
}

export const TournamentDetails = () => {
    const { id } = useParams<{ id: string }>();
    const { user } = useAuth();
    const queryClient = useQueryClient();
    const [showTeamSelect, setShowTeamSelect] = useState(false);

    const { data: tournament, isLoading } = useQuery<Tournament>({
        queryKey: ["tournament", id],
        queryFn: async () => {
            const response = await apiClient.get(`/tournaments/${id}`);
            return response.data;
        },
    });

    const { data: userTeams } = useQuery({
        queryKey: ["user-teams"],
        queryFn: async () => {
            const response = await apiClient.get("/teams/my");
            return response.data;
        },
        enabled: !!user,
    });

    const joinMutation = useMutation({
        mutationFn: async (teamId: number) => {
            const response = await apiClient.post(`/tournaments/${id}/join`, {
                team_id: teamId,
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["tournament", id] });
            setShowTeamSelect(false);
            toast.success("Команда успешно зарегистрирована на турнир");
        },
        onError: (error: any) => {
            const message =
                error.response?.data?.detail ||
                "Не удалось зарегистрировать команду";
            toast.error(message);
            setShowTeamSelect(false);
        },
    });

    const leaveMutation = useMutation({
        mutationFn: async (teamId: number) => {
            const response = await apiClient.post(`/tournaments/${id}/leave`, {
                team_id: teamId,
            });
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["tournament", id] });
            toast.success("Команда снята с участия");
        },
        onError: (error: any) => {
            const message =
                error.response?.data?.detail ||
                "Не удалось снять команду с участия";
            toast.error(message);
        },
    });

    const getStatusBadge = (status: string) => {
        const statusMap = {
            registration: {
                label: "Регистрация",
                variant: "outline" as const,
            },
            in_progress: {
                label: "В процессе",
                variant: "secondary" as const,
            },
            completed: {
                label: "Завершен",
                variant: "default" as const,
            },
        };

        return (
            statusMap[status as keyof typeof statusMap] || {
                label: status,
                variant: "outline" as const,
            }
        );
    };

    const isAdminOrOrganizer =
        user?.role === "ADMIN" || user?.role === "ORGANIZER";

    const updateStatusMutation = useMutation({
        mutationFn: async (newStatus: string) => {
            await apiClient.patch(`/tournaments/${id}/status`, {
                status: newStatus,
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["tournament", id] });
            toast.success("Статус турнира обновлен");
        },
        onError: () => {
            toast.error("Не удалось обновить статус турнира");
        },
    });

    const getStatusActions = () => {
        if (!isAdminOrOrganizer || !tournament) return null;

        switch (tournament.status) {
            case "DRAFT":
                return (
                    <Button
                        onClick={() =>
                            updateStatusMutation.mutate("REGISTRATION")
                        }
                        variant="default"
                    >
                        Открыть регистрацию
                    </Button>
                );
            case "REGISTRATION":
                const hasEnoughTeams = tournament.teams?.length >= 2;
                return (
                    <Button
                        onClick={() =>
                            updateStatusMutation.mutate("IN_PROGRESS")
                        }
                        variant="default"
                        disabled={!hasEnoughTeams}
                        title={
                            !hasEnoughTeams
                                ? "Необходимо минимум 2 команды"
                                : ""
                        }
                    >
                        Начать турнир
                    </Button>
                );
            case "IN_PROGRESS":
                const allMatchesCompleted = tournament.matches?.every(
                    (match: Match) => match.winner_id
                );
                return (
                    <Button
                        onClick={() => updateStatusMutation.mutate("COMPLETED")}
                        variant="default"
                        disabled={!allMatchesCompleted}
                        title={
                            !allMatchesCompleted ? "Не все матчи завершены" : ""
                        }
                    >
                        Завершить турнир
                    </Button>
                );
            default:
                return null;
        }
    };

    const canJoin =
        tournament?.status === "REGISTRATION" && userTeams?.length > 0;
    const userTeamIds = userTeams?.map((team: Team) => team.id) || [];
    const hasTeamInTournament = tournament?.teams?.some((team: Team) =>
        userTeamIds.includes(team.id)
    );

    const getTeamActions = (team: any) => {
        if (!canJoin && !hasTeamInTournament) return null;

        if (userTeamIds.includes(team.id)) {
            return (
                <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => leaveMutation.mutate(team.id)}
                >
                    Отменить участие
                </Button>
            );
        }

        if (canJoin && !hasTeamInTournament) {
            return (
                <Button
                    className="w-full"
                    onClick={() => {
                        if (userTeams?.length === 1) {
                            joinMutation.mutate(userTeams[0].id);
                        } else {
                            setShowTeamSelect(true);
                        }
                    }}
                >
                    Принять участие
                </Button>
            );
        }

        return null;
    };

    if (isLoading) {
        return <div>Загрузка...</div>;
    }

    if (!tournament) {
        return <div>Турнир не найден</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold">{tournament?.name}</h1>
                    <p className="text-muted-foreground">
                        {tournament?.description}
                    </p>
                </div>
                <div className="flex flex-col gap-4">
                    <div className="flex gap-4">
                        <div className="text-right">
                            <div className="text-sm text-muted-foreground">
                                Статус
                            </div>
                            <Badge
                                variant={
                                    getStatusBadge(tournament?.status || "")
                                        .variant
                                }
                            >
                                {getStatusBadge(tournament?.status || "").label}
                            </Badge>
                        </div>
                        <div className="text-right">
                            <div className="text-sm text-muted-foreground">
                                Тип
                            </div>
                            <div className="font-medium">
                                {tournament?.type}
                            </div>
                        </div>
                    </div>
                    {getStatusActions()}
                </div>
            </div>

            {/* Диалог выбора команды */}
            <Dialog open={showTeamSelect} onOpenChange={setShowTeamSelect}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Выберите команду</DialogTitle>
                        <DialogDescription>
                            Выберите команду для участия в турнире
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4">
                        {userTeams?.map((team) => (
                            <Button
                                key={team.id}
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => {
                                    joinMutation.mutate(team.id);
                                    setShowTeamSelect(false);
                                }}
                            >
                                <div className="flex items-center gap-2">
                                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                                        {team.name[0].toUpperCase()}
                                    </div>
                                    <div className="flex flex-col items-start">
                                        <span className="font-medium">
                                            {team.name}
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                            {team.members?.length || 0}{" "}
                                            участников
                                        </span>
                                    </div>
                                </div>
                            </Button>
                        ))}
                    </div>
                </DialogContent>
            </Dialog>

            <div className="grid grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Users className="h-5 w-5" />
                            Участвующие команды
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Название</TableHead>
                                    <TableHead>Участники</TableHead>
                                    <TableHead></TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {tournament?.teams?.length > 0 ? (
                                    tournament.teams.map((team: Team) => (
                                        <TableRow key={team.id}>
                                            <TableCell className="font-medium">
                                                {team.name}
                                            </TableCell>
                                            <TableCell>
                                                {team.members
                                                    ?.map(
                                                        (m: any) => m.username
                                                    )
                                                    .join(", ")}
                                            </TableCell>
                                            <TableCell>
                                                {getTeamActions(team)}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell
                                            colSpan={3}
                                            className="text-center text-muted-foreground"
                                        >
                                            {canJoin && !hasTeamInTournament ? (
                                                <div className="space-y-2">
                                                    <div>
                                                        Нет зарегистрированных
                                                        команд
                                                    </div>
                                                    <Button
                                                        onClick={() => {
                                                            if (
                                                                userTeams?.length ===
                                                                1
                                                            ) {
                                                                joinMutation.mutate(
                                                                    userTeams[0]
                                                                        .id
                                                                );
                                                            } else {
                                                                setShowTeamSelect(
                                                                    true
                                                                );
                                                            }
                                                        }}
                                                    >
                                                        Принять участие
                                                    </Button>
                                                </div>
                                            ) : (
                                                "Нет зарегистрированных команд"
                                            )}
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Trophy className="h-5 w-5" />
                            Матчи
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Раунд</TableHead>
                                    <TableHead>Команды</TableHead>
                                    <TableHead>Статус</TableHead>
                                    <TableHead>Победитель</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {tournament?.matches?.length > 0 ? (
                                    tournament.matches.map((match: Match) => (
                                        <TableRow key={match.id}>
                                            <TableCell>{match.round}</TableCell>
                                            <TableCell>
                                                {
                                                    tournament.teams?.find(
                                                        (t) =>
                                                            t.id ===
                                                            match.team1_id
                                                    )?.name
                                                }{" "}
                                                vs{" "}
                                                {
                                                    tournament.teams?.find(
                                                        (t) =>
                                                            t.id ===
                                                            match.team2_id
                                                    )?.name
                                                }
                                            </TableCell>
                                            <TableCell>
                                                {match.status}
                                            </TableCell>
                                            <TableCell>
                                                {match.winner_id
                                                    ? tournament.teams?.find(
                                                          (t) =>
                                                              t.id ===
                                                              match.winner_id
                                                      )?.name
                                                    : "-"}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell
                                            colSpan={4}
                                            className="text-center text-muted-foreground"
                                        >
                                            Нет матчей
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};
