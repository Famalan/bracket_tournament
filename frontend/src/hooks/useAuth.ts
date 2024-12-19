import { create } from "zustand";
import { apiClient } from "@/api/client";

interface User {
    id: number;
    username: string;
    email: string;
    role: string;
}

interface RegisterData {
    username: string;
    email: string;
    password: string;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    isAdmin: boolean;
    error: string | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => void;
    checkAuth: () => Promise<void>;
    register: (data: RegisterData) => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
    user: JSON.parse(localStorage.getItem("user") || "null"),
    token: localStorage.getItem("token"),
    isAuthenticated: !!localStorage.getItem("token"),
    isAdmin:
        JSON.parse(localStorage.getItem("user") || "null")?.role === "ADMIN",
    isLoading: false,
    error: null,

    register: async (data: RegisterData) => {
        try {
            console.log("Попытка регистрации с данными:", {
                username: data.username,
                password: data.password,
            });

            const formData = new URLSearchParams();
            formData.append("username", data.username.trim());
            formData.append("password", data.password);

            const response = await apiClient.post("/auth/register", formData, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            if (response.data.access_token && response.data.user) {
                localStorage.setItem("token", response.data.access_token);
                set({
                    user: response.data.user,
                    token: response.data.access_token,
                    isAuthenticated: true,
                    isAdmin: response.data.user.role === "ADMIN",
                    error: null,
                });
            } else {
                throw new Error("Некорректный ответ от сервера");
            }

            return response.data;
        } catch (error: any) {
            console.error(
                "Ошибка при регистрации:",
                error.response?.data || error
            );

            const errorMessage =
                error.response?.data?.detail ||
                error.response?.data?.message ||
                error.message ||
                "Произошла ошибка при регистрации";

            throw new Error(errorMessage);
        }
    },

    login: async (username: string, password: string) => {
        try {
            set({ isLoading: true, error: null });

            // Создаем FormData
            const formData = new URLSearchParams();
            formData.append("username", username.trim());
            formData.append("password", password.trim());

            const response = await apiClient.post("/auth/login", formData, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            const { access_token, user } = response.data;

            localStorage.setItem("token", access_token);
            localStorage.setItem("user", JSON.stringify(user));

            set({
                user,
                token: access_token,
                isAuthenticated: true,
                isAdmin: user.role === "ADMIN",
            });
        } catch (error) {
            set({ error: "Неверное имя пользователя или пароль" });
            throw error;
        } finally {
            set({ isLoading: false });
        }
    },

    logout: () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        set({
            user: null,
            token: null,
            isAuthenticated: false,
            isAdmin: false,
        });
    },

    checkAuth: async () => {
        try {
            set({ isLoading: true });
            const response = await apiClient.get("/auth/me");
            const user = response.data.user;

            localStorage.setItem("user", JSON.stringify(user));

            set({
                user,
                isAuthenticated: true,
                isAdmin: user.role === "ADMIN",
                error: null,
            });
        } catch (error) {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            set({
                user: null,
                token: null,
                isAuthenticated: false,
                isAdmin: false,
                error: "Сессия истекла",
            });
        } finally {
            set({ isLoading: false });
        }
    },
}));
