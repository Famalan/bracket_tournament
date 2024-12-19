export type UserRole = "ADMIN" | "ORGANIZER" | "PLAYER";

export interface User {
    id: number;
    username: string;
    email: string;
    role: UserRole;
    created_at: string;
    updated_at: string;
}

export interface Tournament {
    id: number;
    name: string;
    description?: string;
    type: "single_elimination" | "double_elimination" | "round_robin";
    status: string;
    rules?: string;
    max_teams: number;
    registration_deadline: string;
    start_date: string;
    end_date: string;
    created_by: number;
    registered_teams: number;
}

export interface Team {
    id: number;
    name: string;
    description: string;
    logo_url?: string;
}

export interface TeamCreateData {
    name: string;
    description: string;
    logo_url?: string;
}

export interface TournamentCreate {
    name: string;
    description?: string;
    type: "single_elimination" | "double_elimination" | "round_robin";
    rules?: string;
    max_teams: number;
    registration_deadline: string;
    start_date: string;
    end_date: string;
}

export enum TournamentType {
    SINGLE_ELIMINATION = "SINGLE_ELIMINATION",
    DOUBLE_ELIMINATION = "DOUBLE_ELIMINATION",
    ROUND_ROBIN = "ROUND_ROBIN",
}

export enum TournamentStatus {
    DRAFT = "DRAFT",
    REGISTRATION = "REGISTRATION",
    IN_PROGRESS = "IN_PROGRESS",
    COMPLETED = "COMPLETED",
    CANCELLED = "CANCELLED",
}

export interface Match {
    id: number;
    tournament_id: number;
    team1_id: number;
    team2_id: number;
    score_team1: number | null;
    score_team2: number | null;
    winner_id: number | null;
    status: "scheduled" | "in_progress" | "completed" | "cancelled";
    start_time: string;
    end_time: string | null;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User; // Добавлено поле user
}

export interface RegisterData {
    username: string;
    password: string;
}
