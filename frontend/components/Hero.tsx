import Image from "next/image";

export default function Hero() {
  return (
    <section className="relative w-full bg-white flex items-center justify-center py-6 overflow-hidden">
      <p>Impact-Site-Verification: d5150b5f-50f0-49f9-b558-b98ef2b7c402</p>
      {/* Full image, no cropping */}
      <Image
        src="/hero.png"
        alt="Curivao — curated interior design"
        width={1536}
        height={1024}
        className="w-full max-h-[520px] object-contain"
        unoptimized
        priority
      />

    </section>
  );
}
