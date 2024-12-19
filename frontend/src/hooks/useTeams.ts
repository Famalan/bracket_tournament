import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/api/client";
import { useAuth } from "./useAuth";

interface Member {
    id: number;
    username: string;
    email: string;
    role: string;
}

interface Team {
    id: number;
    name: string;
    description: string;
    captain_id: number;
    members: Member[];
}

interface TeamCreateData {
    name: string;
    description?: string;
}

export const useTeams = () => {
    const queryClient = useQueryClient();
    const { user } = useAuth();

    const {
        data: teams,
        isLoading,
        error,
    } = useQuery<Team[]>({
        queryKey: ["teams"],
        queryFn: async () => {
            const response = await apiClient.get("/teams");
            return response.data;
        },
    });

    const createMutation = useMutation({
        mutationFn: async (teamData: TeamCreateData) => {
            const response = await apiClient.post("/teams", teamData);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["teams"] });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: async (teamId: number) => {
            await apiClient.delete(`/teams/${teamId}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["teams"] });
        },
    });

    const handleCreateTeam = async (teamData: TeamCreateData) => {
        try {
            await createMutation.mutateAsync(teamData);
        } catch (err) {
            console.error("Error creating team:", err);
            throw err;
        }
    };

    const handleDeleteTeam = async (teamId: number) => {
        try {
            await deleteMutation.mutateAsync(teamId);
        } catch (err) {
            console.error("Error deleting team:", err);
            throw err;
        }
    };

    return {
        teams,
        handleCreateTeam,
        handleDeleteTeam,
        isLoading:
            isLoading || createMutation.isPending || deleteMutation.isPending,
        error,
        canCreateTeam: user?.role === "ADMIN" || user?.role === "ORGANIZER",
        canDeleteTeam: user?.role === "ADMIN",
    };
};
