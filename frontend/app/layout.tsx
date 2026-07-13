import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "../src/context/auth-context";
import { ThemeProvider } from "../src/context/theme-context";
import { TaskRefreshProvider } from "../src/context/task-refresh-context";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Todo App",
  description: "A simple and intuitive todo application",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} antialiased min-h-screen flex flex-col`}
      >
        <ThemeProvider>
          <AuthProvider>
            <TaskRefreshProvider>
              {/* App wrapper */}
              <div className="flex flex-col min-h-screen">
                {children}
              </div>
            </TaskRefreshProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
