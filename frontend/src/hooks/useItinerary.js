import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getItinerary, getTripStatus } from "@/lib/api";
import { useAppStore } from "@/stores/appStore";
const POLL_INTERVAL_MS = 3000;
const TERMINAL_STATUSES = new Set(["ready", "failed"]);
export function useItinerary(tripId) {
    const setItinerary = useAppStore((s) => s.setItinerary);
    // Poll status until terminal
    const statusQuery = useQuery({
        queryKey: ["tripStatus", tripId],
        queryFn: () => getTripStatus(tripId),
        enabled: !!tripId,
        refetchInterval: (query) => {
            const status = query.state.data?.status;
            return status && TERMINAL_STATUSES.has(status) ? false : POLL_INTERVAL_MS;
        },
    });
    const isReady = statusQuery.data?.status === "ready";
    // Fetch itinerary once ready
    const itineraryQuery = useQuery({
        queryKey: ["itinerary", tripId],
        queryFn: () => getItinerary(tripId),
        enabled: !!tripId && isReady,
    });
    useEffect(() => {
        if (itineraryQuery.data) {
            setItinerary(itineraryQuery.data);
        }
    }, [itineraryQuery.data, setItinerary]);
    return {
        status: statusQuery.data?.status ?? null,
        itinerary: itineraryQuery.data ?? null,
        isLoading: statusQuery.isLoading || itineraryQuery.isLoading,
        error: statusQuery.error ?? itineraryQuery.error,
    };
}
