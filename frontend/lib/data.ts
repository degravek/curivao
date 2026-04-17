/**
 * Server-side data access functions — call Supabase directly.
 * Import only in Server Components and API route handlers.
 */
import { getSupabaseAdmin } from "./supabase-server";
import type { Room, RoomSummary, RoomsResponse } from "./types";

const VALID_LIMITS = new Set([10, 20, 50]);

export async function getRooms(
  limit: number,
  page: number
): Promise<RoomsResponse> {
  if (!VALID_LIMITS.has(limit)) limit = 10;
  const offset = (page - 1) * limit;
  const supabase = getSupabaseAdmin();

  const [roomsRes, countRes] = await Promise.all([
    supabase
      .from("generated_rooms")
      .select(
        "id, design_intent, dominant_style, color_palette, image_url, created_at"
      )
      .eq("published", true)
      .order("created_at", { ascending: false })
      .range(offset, offset + limit - 1),
    supabase
      .from("generated_rooms")
      .select("id", { count: "exact", head: true })
      .eq("published", true),
  ]);

  if (roomsRes.error) throw new Error(roomsRes.error.message);

  return {
    rooms: roomsRes.data as RoomSummary[],
    total: countRes.count ?? 0,
    page,
    limit,
  };
}

export async function getRoom(id: string): Promise<Room | null> {
  const supabase = getSupabaseAdmin();

  const roomRes = await supabase
    .from("generated_rooms")
    .select("*")
    .eq("id", id)
    .limit(1);

  if (roomRes.error) throw new Error(roomRes.error.message);
  if (!roomRes.data || roomRes.data.length === 0) return null;

  const room = roomRes.data[0];
  const pieces: Record<string, unknown>[] = room.selected_pieces ?? [];

  const productIds = pieces
    .map((p) => (p.catalog_id as string) || (p.product_id as string))
    .filter(Boolean);

  let productMap: Record<string, Record<string, unknown>> = {};
  if (productIds.length > 0) {
    const productsRes = await supabase
      .from("products")
      .select("id, name, brand, retailer, product_url, price, currency")
      .in("id", productIds);

    if (productsRes.data) {
      productMap = Object.fromEntries(
        productsRes.data.map((p) => [p.id, p])
      );
    }
  }

  const enrichedPieces = pieces.map((piece) => {
    const pid = (piece.catalog_id as string) || (piece.product_id as string);
    const product = productMap[pid] ?? {};
    return {
      ...piece,
      product_id: pid,
      product_name: (piece.product_name as string) || (piece.name as string),
      placement_note:
        (piece.placement_note as string) || (piece.placement as string),
      price: product.price,
      currency: (product.currency as string) ?? "USD",
      retailer: product.retailer,
      product_url: product.product_url,
    };
  });

  return { ...room, selected_pieces: enrichedPieces } as Room;
}
