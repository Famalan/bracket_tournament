import { useState } from "react";
import { useTeams } from "../hooks/useTeams";
import { DashboardLayout } from "@/components/DashboardLayout";
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
import { Plus, Users, Settings, Trophy } from "lucide-react";
import { Input } from "@/components/ui/input";
import { ManageMembersModal } from "@/components/teams/ManageMembersModal";
import { useAuth } from "@/hooks/useAuth";

export const Teams = () => {
    const { user } = useAuth();
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
    const [showManageMembers, setShowManageMembers] = useState(false);
    const {
        teams,
        handleCreateTeam,
        handleDeleteTeam,
        isLoading,
        error,
        canDeleteTeam,
    } = useTeams();

    const [formData, setFormData] = useState({
        name: "",
        description: "",
    });

    const isAdmin = user?.role === "ADMIN";
    const isOrganizer = user?.role === "ORGANIZER";
    const canCreateTeam = isAdmin || isOrganizer;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await handleCreateTeam(formData);
            setShowCreateForm(false);
            setFormData({ name: "", description: "" });
        } catch (err) {
            console.error("Error creating team:", err);
        }
    };

    const onDeleteTeam = async (teamId: number) => {
        if (window.confirm("Вы уверены, что хотите удалить эту команду?")) {
            try {
                await handleDeleteTeam(teamId);
            } catch (err) {
                console.error("Error deleting team:", err);
            }
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Команды</h1>
                    <p className="text-muted-foreground">
                        Управление командами и их составами
                    </p>
                </div>
                {canCreateTeam && (
                    <Button onClick={() => setShowCreateForm(true)}>
                        Создать команду
                    </Button>
                )}
            </div>
            {showCreateForm && (
                <Card>
                    <CardHeader>
                        <CardTitle>Создание команды</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Название команды
                                </label>
                                <Input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) =>
                                        setFormData({
                                            ...formData,
                                            name: e.target.value,
                                        })
                                    }
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">
                                    Описание
                                </label>
                                <Input
                                    type="text"
                                    value={formData.description}
                                    onChange={(e) =>
                                        setFormData({
                                            ...formData,
                                            description: e.target.value,
                                        })
                                    }
                                />
                            </div>
                            <div className="flex justify-end space-x-2">
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => setShowCreateForm(false)}
                                >
                                    Отмена
                                </Button>
                                <Button type="submit" disabled={isLoading}>
                                    {isLoading ? "Создание..." : "Создать"}
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            {error && (
                <div className="bg-red-50 text-red-500 p-4 rounded-md">
                    {error}
                </div>
            )}

            <Card>
                <CardHeader>
                    <CardTitle>Список команд</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Название команды</TableHead>
                                <TableHead>Описание</TableHead>
                                <TableHead>Участники</TableHead>
                                <TableHead className="text-right">
                                    Действия
                                </TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {teams?.map((team) => (
                                <TableRow key={team.id}>
                                    <TableCell className="font-medium">
                                        {team.name}
                                    </TableCell>
                                    <TableCell>{team.description}</TableCell>
                                    <TableCell>
                                        <div className="flex flex-col gap-1">
                                            {team.members?.length > 0 ? (
                                                team.members.map((member) => (
                                                    <div
                                                        key={member.id}
                                                        className="flex items-center gap-2 text-sm"
                                                    >
                                                        <div
                                                            className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs"
                                                            title={
                                                                member.username
                                                            }
                                                        >
                                                            {member.username[0].toUpperCase()}
                                                        </div>
                                                        <span>
                                                            {member.username}
                                                        </span>
                                                        {team.captain_id ===
                                                            member.id && (
                                                            <span className="text-xs text-muted-foreground">
                                                                (Капитан)
                                                            </span>
                                                        )}
                                                    </div>
                                                ))
                                            ) : (
                                                <span className="text-sm text-muted-foreground">
                                                    Нет участников
                                                </span>
                                            )}
                                        </div>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <div className="flex justify-end gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => {
                                                    setSelectedTeamId(team.id);
                                                    setShowManageMembers(true);
                                                }}
                                            >
                                                Управление
                                            </Button>
                                            {canDeleteTeam && (
                                                <Button
                                                    variant="destructive"
                                                    size="sm"
                                                    onClick={() =>
                                                        onDeleteTeam(team.id)
                                                    }
                                                >
                                                    Удалить
                                                </Button>
                                            )}
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {showManageMembers && selectedTeamId && (
                <ManageMembersModal
                    isOpen={showManageMembers}
                    onClose={() => {
                        setShowManageMembers(false);
                        setSelectedTeamId(null);
                    }}
                    teamId={selectedTeamId}
                />
            )}
        </div>
    );
};
