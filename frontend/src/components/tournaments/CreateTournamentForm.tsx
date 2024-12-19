import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";

const formSchema = z.object({
    name: z.string().min(3, {
        message: "Название должно содержать минимум 3 символа",
    }),
    description: z.string().min(10, {
        message: "Описание должно содержать минимум 10 символов",
    }),
    type: z.enum(["single_elimination", "double_elimination", "round_robin"], {
        required_error: "Выберите тип турнира",
    }),
    max_teams: z.coerce.number().min(2).max(32),
    start_date: z.string().min(1, "Выберите дату начала"),
    end_date: z.string().min(1, "Выберите дату окончания"),
});

export function CreateTournamentForm() {
    const navigate = useNavigate();
    const { toast } = useToast();

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            name: "",
            description: "",
            type: "single_elimination",
            max_teams: 8,
            start_date: "",
            end_date: "",
        },
    });

    const onSubmit = async (data: z.infer<typeof formSchema>) => {
        try {
            console.log("Отправляемые данные:", data);

            // Преобразуем даты в формат ISO
            const formattedData = {
                ...data,
                start_date: new Date(data.start_date).toISOString(),
                end_date: new Date(data.end_date).toISOString(),
            };

            const response = await api.post("tournaments/", formattedData);

            toast({
                title: "Успех",
                description: "Турнир успешно создан",
            });

            navigate("/tournaments");
        } catch (error: any) {
            console.error("Ошибка при создании турнира:", error);

            const errorMessage =
                error.response?.data?.detail?.[0]?.msg ||
                error.response?.data?.detail ||
                "Произошла ошибка при создании турнира";

            toast({
                variant: "destructive",
                title: "Ошибка",
                description: errorMessage,
            });
        }
    };

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Название турнира</FormLabel>
                            <FormControl>
                                <Input {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Описание</FormLabel>
                            <FormControl>
                                <Input {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="type"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Тип турнира</FormLabel>
                            <FormControl>
                                <select
                                    {...field}
                                    className="w-full p-2 border rounded bg-background text-foreground border-input"
                                >
                                    <option value="single_elimination">
                                        Single Elimination
                                    </option>
                                    <option value="double_elimination">
                                        Double Elimination
                                    </option>
                                    <option value="round_robin">
                                        Round Robin
                                    </option>
                                </select>
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="max_teams"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>
                                Максимальное количество команд
                            </FormLabel>
                            <FormControl>
                                <Input type="number" {...field} />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="start_date"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel className="text-lg font-medium">
                                Дата начала турнира
                            </FormLabel>
                            <FormControl>
                                <div className="relative">
                                    <Input
                                        type="datetime-local"
                                        min={new Date()
                                            .toISOString()
                                            .slice(0, 16)}
                                        className="w-full p-3 pl-12 text-lg border-2 rounded-lg bg-background text-foreground border-input hover:border-primary focus:border-primary transition-colors duration-200 ease-in-out shadow-sm"
                                        {...field}
                                        placeholder="Выберите дату и время"
                                    />
                                    <button
                                        type="button"
                                        className="absolute right-4 top-1/2 transform -translate-y-1/2 text-xl text-foreground hover:text-primary transition-colors"
                                        onClick={() => {
                                            const input =
                                                document.querySelector(
                                                    'input[name="start_date"]'
                                                );
                                            if (input) {
                                                input.showPicker();
                                            }
                                        }}
                                    >
                                        📅
                                    </button>
                                </div>
                            </FormControl>
                            <FormDescription className="mt-2 text-sm text-muted-foreground flex items-center gap-2">
                                <span className="text-blue-500">ℹ️</span>
                                Выберите удобные дату и время для начала турнира
                            </FormDescription>
                            <FormMessage className="text-red-500" />
                        </FormItem>
                    )}
                />

                <FormField
                    control={form.control}
                    name="end_date"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel className="text-lg font-medium">
                                Дата окончания турнира
                            </FormLabel>
                            <FormControl>
                                <div className="relative">
                                    <Input
                                        type="datetime-local"
                                        min={new Date()
                                            .toISOString()
                                            .slice(0, 16)}
                                        className="w-full p-3 pl-12 text-lg border-2 rounded-lg bg-background text-foreground border-input hover:border-primary focus:border-primary transition-colors duration-200 ease-in-out shadow-sm"
                                        {...field}
                                        placeholder="Выберите дату и время"
                                    />
                                    <button
                                        type="button"
                                        className="absolute right-4 top-1/2 transform -translate-y-1/2 text-xl text-foreground hover:text-primary transition-colors"
                                        onClick={() => {
                                            const input =
                                                document.querySelector(
                                                    'input[name="end_date"]'
                                                );
                                            if (input) {
                                                input.showPicker();
                                            }
                                        }}
                                    >
                                        📅
                                    </button>
                                </div>
                            </FormControl>
                            <FormDescription className="mt-2 text-sm text-muted-foreground flex items-center gap-2">
                                <span className="text-blue-500">ℹ️</span>
                                Выберите дату и время окончания турнира
                            </FormDescription>
                            <FormMessage className="text-red-500" />
                        </FormItem>
                    )}
                />

                <div className="flex justify-between items-center gap-4">
                    <div className="space-x-2">
                        <Button type="submit" className="bg-primary">
                            Создать турнир
                        </Button>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => navigate("/tournaments")}
                        >
                            Отмена
                        </Button>
                    </div>

                    <div className="space-x-2">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => {
                                form.reset({
                                    name: "",
                                    description: "",
                                    type: "single_elimination",
                                    max_teams: 8,
                                    start_date: "",
                                    end_date: "",
                                });
                            }}
                        >
                            Очистить форму
                        </Button>
                    </div>
                </div>
            </form>
        </Form>
    );
}
