import type { Room, RoomsResponse } from "./types";

// Defaults to relative paths (Next.js API routes on Vercel).
// Set NEXT_PUBLIC_API_URL to point at a standalone FastAPI backend if needed.
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export async function fetchRooms(
  limit: number,
  page: number
): Promise<RoomsResponse> {
  const res = await fetch(
    `${BASE}/api/rooms?limit=${limit}&page=${page}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error(`Failed to fetch rooms: ${res.status}`);
  return res.json();
}

export async function fetchRoom(id: string): Promise<Room> {
  const res = await fetch(`${BASE}/api/rooms/${id}`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error(`Room not found: ${res.status}`);
  return res.json();
}
