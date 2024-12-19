import { z } from "zod";

export const tournamentSchema = z
    .object({
        name: z
            .string()
            .min(3, "Минимум 3 символа")
            .max(100, "Максимум 100 символов"),
        description: z.string().optional(),
        type: z.enum([
            "single_elimination",
            "double_elimination",
            "round_robin",
        ]),
        rules: z.string().optional(),
        max_teams: z
            .number()
            .min(2, "Минимум 2 команды")
            .max(64, "Максимум 64 команды"),
        registration_deadline: z.string().datetime(),
        start_date: z.string().datetime(),
        end_date: z.string().datetime(),
    })
    .refine(
        (data) =>
            new Date(data.registration_deadline) < new Date(data.start_date),
        {
            message: "Дедлайн регистрации должен быть раньше даты начала",
            path: ["registration_deadline"],
        }
    )
    .refine((data) => new Date(data.start_date) < new Date(data.end_date), {
        message: "Дата начала должна быть раньше даты окончания",
        path: ["start_date"],
    });

export type TournamentFormData = z.infer<typeof tournamentSchema>;
