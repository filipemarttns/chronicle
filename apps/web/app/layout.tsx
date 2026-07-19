import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Chronicle",
  description: "Developer Memory Engine console",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <a className="brand" href="/">
            Chronicle
          </a>
          <nav>
            <a href="/">Home</a>
            <a href="/timeline">Timeline</a>
            <a href="/search">Search</a>
          </nav>
        </header>
        <div className="shell">{children}</div>
      </body>
    </html>
  );
}
