import { getSupabaseAdmin } from "@/lib/supabase-server";

const VALID_LIMITS = new Set([10, 20, 50]);

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  let limit = parseInt(searchParams.get("limit") ?? "10", 10);
  const page = Math.max(1, parseInt(searchParams.get("page") ?? "1", 10));

  if (!VALID_LIMITS.has(limit)) limit = 10;
  const offset = (page - 1) * limit;

  const supabase = getSupabaseAdmin();

  const [roomsRes, countRes] = await Promise.all([
    supabase
      .from("generated_rooms")
      .select("id, design_intent, dominant_style, color_palette, image_url, created_at")
      .eq("published", true)
      .order("created_at", { ascending: false })
      .range(offset, offset + limit - 1),
    supabase
      .from("generated_rooms")
      .select("id", { count: "exact", head: true })
      .eq("published", true),
  ]);

  if (roomsRes.error) {
    return Response.json({ error: roomsRes.error.message }, { status: 500 });
  }

  return Response.json({
    rooms: roomsRes.data,
    total: countRes.count ?? 0,
    page,
    limit,
  });
}
