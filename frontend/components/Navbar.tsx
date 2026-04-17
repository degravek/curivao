import Link from "next/link";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-border">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <span
            className="text-4xl leading-none text-gold"
            style={{ fontFamily: "var(--font-dancing)" }}
          >
            C
          </span>
          <span className="text-xl font-semibold tracking-wide text-foreground">
            Curivao
          </span>
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-8">
          <Link href="/" className="text-sm text-foreground hover:text-gold transition-colors">
            Home
          </Link>
          <Link href="/about" className="text-sm text-foreground hover:text-gold transition-colors">
            About
          </Link>
        </nav>
      </div>
    </header>
  );
}

