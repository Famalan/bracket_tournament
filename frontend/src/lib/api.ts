import axios from "axios";
import { Team, TeamCreateData } from "@/types";

// Создаем экземпляр axios с базовым URL и настройками
export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
    headers: {
        "Content-Type": "application/json",
    },
    withCredentials: true,
});

// Добавляем слэш в конце URL, если его нет
api.interceptors.request.use((config) => {
    if (config.url && !config.url.endsWith("/")) {
        config.url += "/";
    }
    return config;
});

// Добавим логирование запросов
api.interceptors.request.use((request) => {
    console.log("Starting Request", {
        url: request.url,
        method: request.method,
        data: request.data,
    });
    return request;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("API Error:", {
            status: error.response?.status,
            data: error.response?.data,
            config: error.config,
        });
        return Promise.reject(error);
    }
);

// Добавляем перехватчик для добавления токена авторизации
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const createTeam = async (teamData: TeamCreateData): Promise<Team> => {
    const response = await api.post("/teams", teamData);
    return response.data;
};

export const deleteTeam = async (teamId: number): Promise<void> => {
    await api.delete(`/teams/${teamId}`);
};

export const getTeams = async (): Promise<Team[]> => {
    const response = await api.get("/teams");
    return response.data;
};

export default api;
