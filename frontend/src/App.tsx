import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { ThemeProvider } from "@/lib/theme";
import { StoreProvider } from "@/lib/store";
import { Header } from "@/components/layout/Header";
import UploadPage from "./pages/UploadPage";
import ImageGenerationPage from "./pages/ImageGenerationPage";
import VideoGenerationPage from "./pages/VideoGenerationPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <StoreProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            {/* Header commented out to focus on the dedicated workflow pages, or kept if it provides essential nav. 
                Given the specific 3-page flow, we might want to keep it minimal or update it. 
                For now keeping it but routes are main focus. */}
            <Header />
            <AnimatePresence mode="wait">
              <Routes>
                <Route path="/" element={<UploadPage />} />
                <Route path="/generate-images/:courseName" element={<ImageGenerationPage />} />
                <Route path="/generate-video/:courseName" element={<VideoGenerationPage />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </AnimatePresence>
          </BrowserRouter>
        </TooltipProvider>
      </StoreProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
