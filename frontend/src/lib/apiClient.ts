import axios from "axios";
import { useAuth } from "@/hooks/useAuth";
import qs from "qs";

export const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
    headers: {
        "Content-Type": "application/json",
    },
    paramsSerializer: (params) => qs.stringify(params),
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
            useAuth.setState({ user: null, isAuthenticated: false });
        }
        return Promise.reject(error);
    }
);
