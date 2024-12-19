import React from "react";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import { useAuth } from "@/contexts/AuthContext";

type FormData = {
    username: string;
    password: string;
};

const LoginForm: React.FC = () => {
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<FormData>();
    const { login } = useAuth();

    const mutation = useMutation({
        mutationFn: login,
        onError: (error) => {
            console.error("Login error:", error);
        },
        onSuccess: (data) => {
            // Обработка успешного входа
            // Сохранение данных пользователя
            // Например:
            // setUser(data.user);
            // localStorage.setItem('token', data.access_token);
        },
    });

    const onSubmit = (data: FormData) => {
        mutation.mutate(data);
    };

    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <div>
                <label>Имя пользователя</label>
                <input {...register("username", { required: true })} />
                {errors.username && <span>Это поле обязательно</span>}
            </div>
            <div>
                <label>Пароль</label>
                <input
                    type="password"
                    {...register("password", { required: true })}
                />
                {errors.password && <span>Это поле обязательно</span>}
            </div>
            <button type="submit">Войти</button>
        </form>
    );
};

export default LoginForm;
