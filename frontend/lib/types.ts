export interface RoomSummary {
  id: string;
  design_intent: string;
  dominant_style: string | null;
  image_url: string | null;
  created_at: string;
}

export interface SelectedPiece {
  product_id: string;
  product_name: string;
  category: string;
  spatial_role: "anchor" | "secondary" | "accent";
  placement_note: string;
  image_url?: string | null;
  price?: number | null;
  currency?: string | null;
  retailer?: string | null;
  product_url?: string | null;
}

export interface Room extends RoomSummary {
  color_palette: string[] | null;
  selected_pieces: SelectedPiece[];
}

export interface RoomsResponse {
  rooms: RoomSummary[];
  total: number;
  page: number;
  limit: number;
}
