import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function OCRPage() {
  return (
    <div className="space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight mb-3 sm:mb-4">OCR Support</h1>
        <p className="text-base sm:text-lg md:text-xl text-muted-foreground">Answer with photos of handwritten notes.</p>
      </div>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Installation</h2>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>pip install learnlock[ocr]</code></pre>
        <p className="text-xs sm:text-sm text-muted-foreground">Installs EasyOCR and Pillow.</p>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Usage</h2>
        <p className="text-sm sm:text-base text-muted-foreground">During study, provide an image path instead of typing:</p>
        <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto text-xs sm:text-sm"><code>{`Challenge: How does backpropagation update weights?

> /home/user/notes/backprop.jpg

Extracting text from image...
Checking relevance...
Extracted: "Backpropagation uses chain rule..."

[Coach analyzes the extracted text]`}</code></pre>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Supported Formats</h2>
        <ul className="list-disc list-inside space-y-1 text-sm sm:text-base text-muted-foreground">
          <li>.png</li>
          <li>.jpg / .jpeg</li>
          <li>.webp</li>
          <li>.bmp</li>
          <li>.gif</li>
        </ul>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">OCR Engines</h2>
        <p className="text-sm sm:text-base text-muted-foreground">LearnLock tries in order:</p>
        <ol className="list-decimal list-inside space-y-2 text-sm sm:text-base text-muted-foreground">
          <li><strong className="text-foreground">EasyOCR</strong> - Better accuracy, works offline</li>
          <li><strong className="text-foreground">Tesseract</strong> - Fallback (requires pytesseract)</li>
        </ol>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Tips for Better OCR</h2>
        <ul className="list-disc list-inside space-y-1 text-sm sm:text-base text-muted-foreground">
          <li>Good lighting - avoid shadows</li>
          <li>High contrast - dark ink on white paper</li>
          <li>Clear handwriting - print style works best</li>
          <li>Straight alignment - keep paper flat</li>
          <li>Crop tightly - remove background</li>
        </ul>
      </section>

      <section className="space-y-3 sm:space-y-4">
        <h2 className="text-xl sm:text-2xl font-semibold">Troubleshooting</h2>
        <div className="space-y-3 sm:space-y-4">
          <div>
            <h3 className="text-base sm:text-lg font-medium">No OCR engine available</h3>
            <pre className="bg-card p-3 sm:p-4 rounded-lg overflow-x-auto mt-2 text-xs sm:text-sm"><code>pip install learnlock[ocr]</code></pre>
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-medium">Image content not related</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">The extracted text does not match the concept. Check the image or try clearer notes.</p>
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-medium">No text found</h3>
            <p className="text-xs sm:text-sm text-muted-foreground">Try better lighting, higher resolution, or clearer handwriting.</p>
          </div>
        </div>
      </section>

      <div className="p-3 sm:p-4 rounded-lg border border-border/50 bg-card/50">
        <p className="text-xs sm:text-sm text-muted-foreground mb-2">Next:</p>
        <Link href="/docs/configuration" className="inline-flex items-center gap-2 text-sm sm:text-base text-foreground hover:underline font-medium">
          Configuration <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
