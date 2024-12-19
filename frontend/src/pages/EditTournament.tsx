import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { TournamentFormData } from "@/schemas/tournament";
import { useForm } from "react-hook-form";
import { useToast } from "@/hooks/use-toast";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export function EditTournament() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { toast } = useToast();

    const { data: tournament, isLoading } = useQuery({
        queryKey: ["tournament", id],
        queryFn: async () => {
            const { data } = await api.get(`/tournaments/${id}`);
            return data;
        },
        enabled: !!id,
    });

    const mutation = useMutation({
        mutationFn: async (data: Partial<TournamentFormData>) => {
            const response = await api.patch(`/tournaments/${id}`, data);
            return response.data;
        },
        onSuccess: () => {
            toast({
                title: "Успех",
                description: "Турнир успешно обновлен",
            });
            navigate("/tournaments");
        },
        onError: (error: any) => {
            toast({
                variant: "destructive",
                title: "Ошибка",
                description:
                    error.response?.data?.detail ||
                    "Произошла ошибка при обновлении турнира",
            });
        },
    });

    const { register, handleSubmit } = useForm<TournamentFormData>({
        defaultValues: tournament,
    });

    const onSubmit = (data: TournamentFormData) => {
        mutation.mutate(data);
    };

    if (isLoading) return <div>Загрузка...</div>;

    return (
        <ErrorBoundary>
            <div className="container mx-auto py-6">
                <h1 className="text-3xl font-bold mb-4">
                    Редактировать турнир
                </h1>
                <form
                    onSubmit={handleSubmit(onSubmit)}
                    className="max-w-2xl space-y-6"
                >
                    <div>
                        <label className="block text-sm font-medium mb-1">
                            Название
                        </label>
                        <Input {...register("name")} />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">
                            Описание
                        </label>
                        <Textarea {...register("description")} rows={4} />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">
                            Тип турнира
                        </label>
                        <select
                            {...register("type")}
                            className="w-full p-2 border rounded bg-background text-foreground border-input"
                        >
                            <option value="single_elimination">
                                Single Elimination
                            </option>
                            <option value="double_elimination">
                                Double Elimination
                            </option>
                            <option value="round_robin">Round Robin</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-1">
                            Максимальное количество команд
                        </label>
                        <input
                            type="number"
                            {...register("max_teams")}
                            className="w-full p-2 border rounded bg-background text-foreground border-input"
                        />
                    </div>

                    <div className="flex gap-4">
                        <button
                            type="submit"
                            className="px-4 py-2 bg-primary text-white rounded"
                            disabled={mutation.isPending}
                        >
                            {mutation.isPending
                                ? "Сохранение..."
                                : "Сохранить изменения"}
                        </button>
                        <button
                            type="button"
                            onClick={() => navigate("/tournaments")}
                            className="px-4 py-2 bg-secondary text-secondary-foreground rounded"
                        >
                            Отмена
                        </button>
                    </div>
                </form>
            </div>
        </ErrorBoundary>
    );
}
