import type { NextRequest } from "next/server";
import { getRoom } from "@/lib/data";

export async function GET(
  _req: NextRequest,
  ctx: RouteContext<"/api/rooms/[id]">
) {
  const { id } = await ctx.params;

  try {
    const room = await getRoom(id);
    if (!room) {
      return Response.json({ error: "Room not found" }, { status: 404 });
    }
    return Response.json(room);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return Response.json({ error: message }, { status: 500 });
  }
}
