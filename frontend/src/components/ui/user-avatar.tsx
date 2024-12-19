import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { User } from "@/types";

interface UserAvatarProps {
    user: User | null;
}

export function UserAvatar({ user }: UserAvatarProps) {
    if (!user || !user.username) return null;

    return (
        <Avatar>
            <AvatarFallback>
                {user.username.slice(0, 2).toUpperCase()}
            </AvatarFallback>
        </Avatar>
    );
}
