import { Suspense } from "react";
import { fetchRooms } from "@/lib/api";
import Hero from "@/components/Hero";
import RoomGrid from "@/components/RoomGrid";

interface PageProps {
  searchParams: Promise<{ limit?: string; page?: string }>;
}

export default async function Home({ searchParams }: PageProps) {
  const params = await searchParams;
  const limit = Number(params.limit) || 10;
  const page = Number(params.page) || 1;

  let data;
  try {
    data = await fetchRooms(limit, page);
  } catch {
    data = { rooms: [], total: 0, page: 1, limit };
  }

  return (
    <>
      <Hero />
      <Suspense>
        <RoomGrid
          rooms={data.rooms}
          total={data.total}
          page={data.page}
          limit={data.limit}
        />
      </Suspense>
    </>
  );
}
