import { Sidebar } from "@/components/layout/sidebar";
import { DocsPageTransition } from "@/components/layout/docs-page-transition";

export default function DocsLayout({ children }: { children: React.ReactNode }) {

  return (
    <div className="flex flex-col min-h-[calc(100vh-3.5rem)] font-[Varela_Round]">
      {/* Mobile Documentation label only */}
      <div className="md:hidden px-4 pt-4">
        <span className="text-sm font-semibold text-muted-foreground">
          Documentation
        </span>
      </div>
      
      <div className="flex flex-1">
        {/* Fixed Sidebar - Desktop */}
        <aside className="fixed left-0 top-14 z-30 hidden h-[calc(100vh-3.5rem)] w-55 shrink-0 border-r border-border/50 bg-background md:block lg:w-65 xl:w-70">
          <div className="h-full overflow-y-auto py-6 px-3 lg:px-4 lg:py-8">
            <Sidebar />
          </div>
        </aside>
        
        {/* Main Content - offset by sidebar width */}
        <main className="flex-1 w-full md:ml-55 lg:ml-65 xl:ml-70">
          <div className="py-4 px-4 sm:py-6 sm:px-6 lg:py-8 lg:px-8">
            <div className="mx-auto w-full max-w-3xl lg:max-w-4xl">
              <DocsPageTransition>{children}</DocsPageTransition>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
