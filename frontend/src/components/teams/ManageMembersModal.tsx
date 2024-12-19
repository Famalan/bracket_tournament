import { useState, useEffect } from "react";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/api/client";
import { User } from "@/types";

interface ManageMembersModalProps {
    isOpen: boolean;
    onClose: () => void;
    teamId: number;
}

export function ManageMembersModal({
    isOpen,
    onClose,
    teamId,
}: ManageMembersModalProps) {
    const [members, setMembers] = useState<User[]>([]);
    const [availableUsers, setAvailableUsers] = useState<User[]>([]);
    const [selectedUserId, setSelectedUserId] = useState<string>("");
    const { toast } = useToast();

    useEffect(() => {
        if (isOpen) {
            fetchMembers();
            fetchAvailableUsers();
        }
    }, [isOpen, teamId]);

    const fetchMembers = async () => {
        try {
            const response = await apiClient.get(`/teams/${teamId}/members`);
            setMembers(response.data);
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Ошибка",
                description: "Не удалось загрузить список участников",
            });
        }
    };

    const fetchAvailableUsers = async () => {
        try {
            const response = await apiClient.get("/users");
            const allUsers = response.data;
            // Фильтруем пользователей, которые еще не в команде
            const availableUsers = allUsers.filter(
                (user: User) => !members.some((member) => member.id === user.id)
            );
            setAvailableUsers(availableUsers);
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Ошибка",
                description: "Не удалось загрузить список пользователей",
            });
        }
    };

    const handleAddMember = async () => {
        if (!selectedUserId) return;

        try {
            await apiClient.post(`/teams/${teamId}/members`, {
                user_id: parseInt(selectedUserId),
            });
            setSelectedUserId("");
            fetchMembers();
            fetchAvailableUsers();
            toast({
                title: "Успех",
                description: "Участник добавлен в команду",
            });
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Ошибка",
                description: "Не удалось добавить участника",
            });
        }
    };

    const handleRemoveMember = async (userId: number) => {
        try {
            await apiClient.delete(`/teams/${teamId}/members/${userId}`);
            fetchMembers();
            fetchAvailableUsers();
            toast({
                title: "Успех",
                description: "Участник удален из команды",
            });
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Ошибка",
                description: "Не удалось удалить участника",
            });
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Управление участниками команды</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                    <div className="flex gap-2">
                        <Select
                            value={selectedUserId}
                            onValueChange={setSelectedUserId}
                        >
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Выберите пользователя" />
                            </SelectTrigger>
                            <SelectContent>
                                {availableUsers.map((user) => (
                                    <SelectItem
                                        key={user.id}
                                        value={user.id.toString()}
                                    >
                                        {user.username}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <Button
                            onClick={handleAddMember}
                            disabled={!selectedUserId}
                        >
                            Добавить
                        </Button>
                    </div>
                    <div className="space-y-2">
                        {members.map((member) => (
                            <div
                                key={member.id}
                                className="flex items-center justify-between p-2 border rounded"
                            >
                                <span>{member.username}</span>
                                <Button
                                    variant="destructive"
                                    size="sm"
                                    onClick={() =>
                                        handleRemoveMember(member.id)
                                    }
                                >
                                    Удалить
                                </Button>
                            </div>
                        ))}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
