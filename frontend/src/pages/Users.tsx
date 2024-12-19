import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Shield, User, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

const roleLabels: Record<string, string> = {
    ADMIN: "Администратор",
    ORGANIZER: "Организатор",
    PLAYER: "Игрок",
};

export function Users() {
    const { toast } = useToast();
    const { data: users, refetch } = useQuery({
        queryKey: ["users"],
        queryFn: async () => {
            const { data } = await api.get("/users");
            return data;
        },
    });

    const updateRoleMutation = useMutation({
        mutationFn: async ({
            userId,
            role,
        }: {
            userId: number;
            role: string;
        }) => {
            const { data } = await api.patch(`/users/${userId}/role`, { role });
            return data;
        },
        onSuccess: () => {
            toast({
                title: "Успех",
                description: "Роль пользователя успешно обновлена",
            });
            refetch();
        },
        onError: (error: any) => {
            toast({
                variant: "destructive",
                title: "Ошибка",
                description:
                    error.response?.data?.detail ||
                    "Произошла ошибка при обновлении роли",
            });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: async (userId: number) => {
            await api.delete(`/users/${userId}`);
        },
        onSuccess: () => {
            toast({
                title: "Успех",
                description: "Пользователь успешно удален",
            });
            refetch();
        },
        onError: (error: any) => {
            toast({
                variant: "destructive",
                title: "Ошибка",
                description:
                    error.response?.data?.detail ||
                    "Произошла ошибка при удалении пользователя",
            });
        },
    });

    const handleDelete = async (userId: number) => {
        if (
            window.confirm("Вы уверены, что хотите удалить этого пользователя?")
        ) {
            await deleteMutation.mutate(userId);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Пользователи</h1>
                    <p className="text-muted-foreground">
                        Управление ролями пользователей
                    </p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Список пользователей</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {users?.map((user: any) => (
                            <div
                                key={user.id}
                                className="flex items-center justify-between p-4 border rounded-lg bg-card"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                        <User className="h-5 w-5 text-primary" />
                                    </div>
                                    <div>
                                        <p className="font-medium">
                                            {user.username}
                                        </p>
                                        <p className="text-sm text-muted-foreground">
                                            {user.email}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    <div className="flex items-center gap-2">
                                        <Shield className="h-4 w-4 text-muted-foreground" />
                                        <Select
                                            defaultValue={user.role}
                                            onValueChange={(role) => {
                                                updateRoleMutation.mutate({
                                                    userId: user.id,
                                                    role: role.toUpperCase(),
                                                });
                                            }}
                                        >
                                            <SelectTrigger className="w-[180px] bg-background">
                                                <SelectValue>
                                                    {roleLabels[user.role] ||
                                                        user.role}
                                                </SelectValue>
                                            </SelectTrigger>
                                            <SelectContent className="bg-background border border-border">
                                                <SelectItem
                                                    value="PLAYER"
                                                    className="hover:bg-accent"
                                                >
                                                    Игрок
                                                </SelectItem>
                                                <SelectItem
                                                    value="ORGANIZER"
                                                    className="hover:bg-accent"
                                                >
                                                    Организатор
                                                </SelectItem>
                                                <SelectItem
                                                    value="ADMIN"
                                                    className="hover:bg-accent"
                                                >
                                                    Администратор
                                                </SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <Button
                                            variant="destructive"
                                            size="icon"
                                            onClick={() =>
                                                handleDelete(user.id)
                                            }
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
