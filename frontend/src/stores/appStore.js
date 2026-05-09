import { create } from "zustand";
import { persist } from "zustand/middleware";
export const useAppStore = create()(persist((set) => ({
    userId: "test-user-1",
    tripId: null,
    teb: null,
    itinerary: null,
    messages: [],
    setUserId: (userId) => set({ userId }),
    setTripId: (tripId) => set({ tripId }),
    setTeb: (teb) => set({ teb }),
    setItinerary: (itinerary) => set({ itinerary }),
    addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
    clearMessages: () => set({ messages: [] }),
}), {
    name: "roamly-store",
    partialize: (state) => ({ tripId: state.tripId }),
}));
