import { Link } from "react-router-dom";

export function Navbar() {
    return (
        <nav className="border-b bg-background">
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                <Link to="/" className="text-2xl font-bold">
                    E-Sport Symphony
                </Link>
            </div>
        </nav>
    );
}
