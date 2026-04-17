"use client";

import { useRouter, useSearchParams } from "next/navigation";
import type { RoomSummary } from "@/lib/types";
import RoomCard from "./RoomCard";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface RoomGridProps {
  rooms: RoomSummary[];
  total: number;
  page: number;
  limit: number;
}

const LIMIT_OPTIONS = [10, 20, 50] as const;

export default function RoomGrid({ rooms, total, page, limit }: RoomGridProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const totalPages = Math.max(1, Math.ceil(total / limit));

  function navigate(nextPage: number, nextLimit: number) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(nextPage));
    params.set("limit", String(nextLimit));
    router.push(`/?${params.toString()}#browse`);
  }

  return (
    <section id="browse" className="max-w-7xl mx-auto px-6 py-16">
      {/* Section heading */}
      <div className="text-center mb-10">
        <h2 className="text-2xl font-bold text-foreground">Browse The Range</h2>
        <p className="text-sm text-muted mt-2">
          AI-designed rooms built from furniture you can actually buy.
        </p>
      </div>

      {rooms.length === 0 ? (
        <p className="text-center text-muted py-24">
          No rooms published yet — check back soon.
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {rooms.map((room) => (
            <RoomCard key={room.id} room={room} />
          ))}
        </div>
      )}

      {/* Pagination controls */}
      <div className="mt-12 flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Show N selector */}
        <div className="flex items-center gap-2 text-sm text-muted">
          <span>Show:</span>
          {LIMIT_OPTIONS.map((n) => (
            <button
              key={n}
              onClick={() => navigate(1, n)}
              className={`px-3 py-1 border rounded text-sm transition-colors ${
                limit === n
                  ? "border-gold bg-gold text-white"
                  : "border-border text-foreground hover:border-gold hover:text-gold"
              }`}
            >
              {n}
            </button>
          ))}
        </div>

        {/* Page navigation */}
        <div className="flex items-center gap-3">
          <button
            disabled={page <= 1}
            onClick={() => navigate(page - 1, limit)}
            className="p-2 border border-border rounded hover:border-gold hover:text-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            aria-label="Previous page"
          >
            <ChevronLeft size={16} />
          </button>
          <span className="text-sm text-muted">
            {page} / {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => navigate(page + 1, limit)}
            className="p-2 border border-border rounded hover:border-gold hover:text-gold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            aria-label="Next page"
          >
            <ChevronRight size={16} />
          </button>
        </div>

        {/* Total count */}
        <p className="text-sm text-muted">
          {total} room{total !== 1 ? "s" : ""} total
        </p>
      </div>
    </section>
  );
}
