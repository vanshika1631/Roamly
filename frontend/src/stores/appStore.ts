import { create } from "zustand";
import type {
  ConversationMessage,
  Itinerary,
  TravelEmotionalBrief,
} from "@/lib/types";
import { persist } from "zustand/middleware";

interface AppState {
  // Auth
  userId: string | null;
  setUserId: (id: string) => void;

  // Intake conversation
  messages: ConversationMessage[];
  addMessage: (msg: ConversationMessage) => void;
  clearMessages: () => void;

  // TEB
  teb: TravelEmotionalBrief | null;
  setTeb: (teb: TravelEmotionalBrief) => void;

  // Active trip
  tripId: string | null;
  setTripId: (id: string) => void;

  // Itinerary
  itinerary: Itinerary | null;
  setItinerary: (it: Itinerary) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      userId: "test-user-1",
      tripId: null,
      teb: null,
      itinerary: null,
      messages: [],
      setUserId: (userId: string) => set({ userId }),
      setTripId: (tripId: string) => set({ tripId }),
      setTeb: (teb: TravelEmotionalBrief) => set({ teb }),
      setItinerary: (itinerary: Itinerary) => set({ itinerary }),
      addMessage: (msg: ConversationMessage) =>
        set((s) => ({ messages: [...s.messages, msg] })),
      clearMessages: () => set({ messages: [] }),
    }),
    {
      name: "roamly-store",
      partialize: (state) => ({ tripId: state.tripId }),
    },
  ),
);
