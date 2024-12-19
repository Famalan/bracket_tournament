// Этот файл создает и настраивает экземпляр axios для взаимодействия с API.
// Он выполняет следующие функции:
// 1. Создает базовый клиент axios с настроенным URL API и заголовками
// 2. Добавляет перехватчик запросов для автоматического добавления токена аутентификации
// 3. Добавляет перехватчик ответов для обработки ошибок аутентификации (401)
//    и автоматического выхода пользователя из системы

import axios from "axios";
import { useAuth } from "@/hooks/useAuth";

export const apiClient = axios.create({
    baseURL: "http://localhost:8000/api/v1",
    headers: {
        "Content-Type": "application/json",
    },
});

apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            useAuth.getState().logout();

            if (!window.location.pathname.includes("/login")) {
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);
