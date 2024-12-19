import { User } from "@/types";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

interface UsersListProps {
    users: User[];
}

// Создаем словарь для красивого отображения ролей
const roleLabels: Record<string, string> = {
    ADMIN: "Администратор",
    ORGANIZER: "Организатор",
    PLAYER: "Игрок",
};

export function UsersList({ users }: UsersListProps) {
    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Имя пользователя</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Роль</TableHead>
                    <TableHead>Дата регистрации</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {users.map((user) => (
                    <TableRow key={user.id}>
                        <TableCell>{user.id}</TableCell>
                        <TableCell>{user.username}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>
                            {roleLabels[user.role] || user.role}
                        </TableCell>
                        <TableCell>
                            {new Date(user.created_at).toLocaleDateString()}
                        </TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    );
}
