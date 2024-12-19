import { Trophy, Users, Calendar, Settings, Home, UserCog } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";

export const Sidebar = () => {
    const location = useLocation();
    const { user } = useAuth();

    console.log("Current user role:", user?.role);

    const isAdmin = user?.role === "ADMIN";
    const isOrganizer = user?.role === "ORGANIZER";

    let menuItems = [
        { icon: Home, label: "Главная", path: "/" },
        { icon: Trophy, label: "Турниры", path: "/tournaments" },
        { icon: Users, label: "Команды", path: "/teams" },
        // { icon: Calendar, label: "Расписание", path: "/schedule" },
        // { icon: Settings, label: "Настройки", path: "/settings" },
    ];

    if (isAdmin) {
        menuItems.push({
            icon: UserCog,
            label: "Пользователи",
            path: "/users",
        });
    }

    return (
        <div className="h-full border-r bg-background flex flex-col">
            <div className="p-6 border-b">
                <Link to="/" className="flex items-center gap-2">
                    <Trophy className="w-6 h-6 text-primary" />
                    <span className="text-xl font-bold">E-Sport Symphony</span>
                </Link>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {menuItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.label}
                            to={item.path}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors",
                                isActive
                                    ? "bg-primary text-primary-foreground"
                                    : "text-muted-foreground hover:bg-secondary/80 hover:text-foreground"
                            )}
                        >
                            <item.icon className="w-5 h-5" />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>
        </div>
    );
};
