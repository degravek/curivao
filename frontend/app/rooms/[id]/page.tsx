import Image from "next/image";
import Link from "next/link";
import { getRoom } from "@/lib/data";
import { ArrowLeft, ExternalLink } from "lucide-react";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function RoomPage({ params }: PageProps) {
  const { id } = await params;

  const room = await getRoom(id).catch(() => null);
  if (!room) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-24 text-center">
        <p className="text-muted mb-4">Room not found.</p>
        <Link href="/" className="text-sm text-gold hover:underline">
          ← Back to feed
        </Link>
      </div>
    );
  }

  const colorPalette = room.color_palette ?? [];
  const pieces = room.selected_pieces ?? [];

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      {/* Back link */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-gold transition-colors mb-8"
      >
        <ArrowLeft size={14} />
        Back to feed
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Room image */}
        <div className="relative aspect-video w-full overflow-hidden bg-surface">
          {room.image_url ? (
            <Image
              src={room.image_url}
              alt={room.design_intent}
              fill
              className="object-cover object-center"
              priority
              sizes="(max-width: 1024px) 100vw, 50vw"
            />
          ) : (
            <div className="absolute inset-0 bg-border flex items-center justify-center">
              <span className="text-muted">No image available</span>
            </div>
          )}
        </div>

        {/* Room details */}
        <div>
          {/* Style badge */}
          {room.dominant_style && (
            <p className="text-xs uppercase tracking-widest text-muted mb-2">
              {room.dominant_style}
            </p>
          )}

          <h1 className="text-xs font-light italic text-muted mb-6 leading-relaxed">
            {room.design_intent}
          </h1>

          {/* Color palette */}
          {colorPalette.length > 0 && (
            <div className="mb-8">
              <p className="text-xs uppercase tracking-widest text-muted mb-2">
                Color palette
              </p>
              <div className="flex flex-wrap gap-2">
                {colorPalette.map((color) => (
                  <span
                    key={color}
                    className="text-xs px-3 py-1 border border-border rounded-full text-foreground/80"
                  >
                    {color}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Products */}
          <div>
            <p className="text-xs uppercase tracking-widest text-muted mb-4">
              Pieces in this room
            </p>
            <div className="divide-y divide-border">
              {pieces.map((piece) => (
                <div key={piece.product_id} className="py-4 flex gap-4 items-start">
                  {/* Product thumbnail */}
                  {piece.image_url && (
                    <div className="relative w-16 h-16 flex-shrink-0 overflow-hidden bg-surface border border-border">
                      <Image
                        src={piece.image_url}
                        alt={piece.product_name}
                        fill
                        className="object-cover"
                        sizes="64px"
                      />
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-sm font-medium text-foreground">
                          {piece.product_name}
                        </p>
                        <p className="text-xs text-muted capitalize mt-0.5">
                          {piece.category}
                          {piece.retailer && ` · ${piece.retailer}`}
                        </p>
                      </div>
                      {piece.price != null && (
                        <p className="text-sm font-semibold text-foreground shrink-0">
                          ${piece.price.toFixed(2)}
                        </p>
                      )}
                    </div>
                    {piece.product_url && (
                      <a
                        href={piece.product_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 mt-2 text-xs text-gold hover:underline font-medium"
                      >
                        Shop at {piece.retailer ?? "retailer"}
                        <ExternalLink size={11} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* CTA — shop the look */}
          <div className="mt-8 pt-6 border-t border-border">
            <p className="text-sm text-muted mb-4">
              Find these pieces and more at your favourite retailers.
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 bg-gold text-white text-sm font-semibold px-6 py-3 uppercase tracking-widest hover:bg-gold-dark transition-colors"
            >
              Browse More Rooms
              <ExternalLink size={14} />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
