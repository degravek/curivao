import type { NextRequest } from "next/server";
import { getSupabaseAdmin } from "@/lib/supabase-server";

export async function GET(
  _req: NextRequest,
  ctx: RouteContext<"/api/rooms/[id]">
) {
  const { id } = await ctx.params;
  const supabase = getSupabaseAdmin();

  const roomRes = await supabase
    .from("generated_rooms")
    .select("*")
    .eq("id", id)
    .limit(1);

  if (roomRes.error) {
    return Response.json({ error: roomRes.error.message }, { status: 500 });
  }
  if (!roomRes.data || roomRes.data.length === 0) {
    return Response.json({ error: "Room not found" }, { status: 404 });
  }

  const room = roomRes.data[0];
  const pieces: Record<string, unknown>[] = room.selected_pieces ?? [];

  // Pieces stored by the image gen agent use "catalog_id"; selection agent uses "product_id"
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

  return Response.json({ ...room, selected_pieces: enrichedPieces });
}
