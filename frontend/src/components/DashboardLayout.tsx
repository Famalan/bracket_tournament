import { ReactNode, useEffect } from "react";
import { Sidebar } from "./Sidebar";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { UserAvatar } from "@/components/ui/user-avatar";

interface DashboardLayoutProps {
    children: ReactNode;
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
    const { logout, user, isLoading, checkAuth } = useAuth();

    useEffect(() => {
        if (!user) {
            checkAuth();
        }
    }, [user, checkAuth]);

    return (
        <div className="flex min-h-screen bg-background">
            <div className="hidden md:flex w-72 flex-col fixed inset-y-0">
                <Sidebar />
            </div>
            <div className="flex-1 flex flex-col md:pl-80">
                <header className="border-b sticky top-0 z-10 bg-background">
                    <div className="container flex h-16 items-center justify-end px-6">
                        {isLoading ? (
                            <div className="animate-pulse flex items-center gap-2">
                                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                                <div className="flex flex-col gap-1">
                                    <div className="w-20 h-4 bg-gray-200 rounded"></div>
                                    <div className="w-16 h-3 bg-gray-200 rounded"></div>
                                </div>
                            </div>
                        ) : user ? (
                            <div className="flex items-center gap-4">
                                <UserAvatar user={user} />
                                <span className="font-medium text-base">
                                    {user.username}
                                </span>
                                <Button variant="outline" onClick={logout}>
                                    Выйти
                                </Button>
                            </div>
                        ) : null}
                    </div>
                </header>
                <main className="flex-1">
                    <div className="container py-8 px-6">{children}</div>
                </main>
            </div>
        </div>
    );
};
