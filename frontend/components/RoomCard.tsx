import Image from "next/image";
import Link from "next/link";
import type { RoomSummary } from "@/lib/types";

export default function RoomCard({ room }: { room: RoomSummary }) {
  return (
    <Link href={`/rooms/${room.id}`} className="group block overflow-hidden">
      {/* Square image */}
      <div className="relative aspect-video overflow-hidden bg-surface">
        {room.image_url ? (
          <Image
            src={room.image_url}
            alt={room.design_intent}
            fill
            className="object-cover object-center transition-transform duration-500 group-hover:scale-105"
            sizes="(max-width: 768px) 100vw, 50vw"
          />
        ) : (
          <div className="absolute inset-0 bg-border flex items-center justify-center">
            <span className="text-muted text-sm">No image</span>
          </div>
        )}

        {/* Hover overlay */}
        <div className="absolute inset-0 bg-foreground/0 group-hover:bg-foreground/20 transition-colors duration-300" />
      </div>

    </Link>
  );
}
