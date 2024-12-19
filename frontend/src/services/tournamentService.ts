import { apiClient } from "@/lib/apiClient";
import { Tournament, TournamentCreate } from "@/types";

export const tournamentService = {
    async getAll() {
        const { data } = await apiClient.get<Tournament[]>("/tournaments");
        return data;
    },

    async getById(id: string) {
        const { data } = await apiClient.get<Tournament>(`/tournaments/${id}`);
        return data;
    },

    async create(tournament: TournamentCreate) {
        const { data } = await apiClient.post<Tournament>(
            "/tournaments",
            tournament
        );
        return data;
    },

    async update(id: string, tournament: Partial<Tournament>) {
        const { data } = await apiClient.patch<Tournament>(
            `/tournaments/${id}`,
            tournament
        );
        return data;
    },

    async delete(id: string) {
        await apiClient.delete(`/tournaments/${id}`);
    },
};
