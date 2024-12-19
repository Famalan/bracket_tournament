import { User } from "@/types";

declare global {
    namespace Express {
        interface Request {
            user?: {
                id: number;
                username: string;
                email: string;
                role: "ADMIN" | "USER" | "ORGANIZER" | "PLAYER";
            };
        }
    }
}
