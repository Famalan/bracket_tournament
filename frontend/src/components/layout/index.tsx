import { useAuth } from "@/contexts/AuthContext";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { Outlet } from "react-router-dom";

export default function Layout() {
    const { user } = useAuth();

    return (
        <div className="min-h-screen bg-background">
            <Navbar user={user} />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
} 