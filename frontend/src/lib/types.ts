// ── Travel Emotional Brief ────────────────────────────────────────────────────

export type TravelMood =
  | "restorative"
  | "adventurous"
  | "celebratory"
  | "exploratory"
  | "romantic";

export type EnergyLevel = "low" | "medium" | "high";
export type SocialContext = "solo" | "couple" | "group" | "family";
export type PopularityTier =
  | "hidden_gem"
  | "local_favourite"
  | "well_known"
  | "tourist_trap";

export interface TravelEmotionalBrief {
  travel_mood: TravelMood;
  energy_level: EnergyLevel;
  social_context: SocialContext;
  motivation: string;
  stimulation_preference: EnergyLevel;
  risk_appetite: EnergyLevel;
  soft_constraints: string[];
  deal_breakers: string[];
  confidence_score: number;
}

// ── Conversation ──────────────────────────────────────────────────────────────

export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
}

// ── Trip ──────────────────────────────────────────────────────────────────────

export type TripStatus =
  | "pending"
  | "generating"
  | "auditing"
  | "ready"
  | "failed";

export interface TripConstraints {
  departure_city: string;
  destination: string;
  start_date: string;
  end_date: string;
  total_budget_usd: number;
  traveler_count: number;
}

export interface TripStatusResponse {
  trip_id: string;
  status: TripStatus;
}

// ── Itinerary ─────────────────────────────────────────────────────────────────

export interface ItineraryStop {
  name: string;
  place_id: string | null;
  category: string;
  address: string | null;
  lat: number | null;
  lng: number | null;
  duration_minutes: number;
  teb_explanation: string;
  popularity_tier: PopularityTier;
}

export interface ItineraryDay {
  day_number: number;
  date: string;
  theme: string;
  stops: ItineraryStop[];
}

export interface Itinerary {
  trip_id: string;
  destination: string;
  days: ItineraryDay[];
  teb_snapshot: TravelEmotionalBrief;
  audit_passed: boolean;
}
