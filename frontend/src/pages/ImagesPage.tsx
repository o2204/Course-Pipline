import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  RefreshCw, Copy, Check, ArrowRight, ArrowLeft, Loader2, 
  ImageIcon, Search, Grid3X3 
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useStore } from "@/lib/store";
import { PageTransition } from "@/components/layout/PageTransition";
import { StepIndicator } from "@/components/layout/StepIndicator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";

interface ImageData {
  videoNumber: number;
  imageIndex: number;
  imageUrl: string;
}

export default function ImagesPage() {
  const navigate = useNavigate();
  const { courseData, setCourseData } = useStore();
  const [fileId, setFileId] = useState(courseData?.fileId || "");
  const [videoNumber, setVideoNumber] = useState<string>("");
  const [images, setImages] = useState<ImageData[]>([]);
  const [courseName, setCourseName] = useState(courseData?.courseName || "");
  const [isLoading, setIsLoading] = useState(false);
  const [regeneratingIndex, setRegeneratingIndex] = useState<string | null>(null);
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);

  useEffect(() => {
    if (courseData?.fileId && !images.length) {
      fetchImages(courseData.fileId);
    }
  }, [courseData?.fileId]);

  const fetchImages = async (id: string, vidNum?: string) => {
    setIsLoading(true);
    try {
      let url = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/get-images/${id}`;
      if (vidNum && vidNum.trim()) {
        url += `?videoNumber=${vidNum}`;
      }
      const response = await fetch(url);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to fetch images");
      }

      const data = await response.json();
      // Map snake_case from API to camelCase for frontend
      const mappedImages = (data.images || []).map((img: any) => ({
        videoNumber: img.video_number,
        imageIndex: img.image_index,
        imageUrl: img.image_url,
      }));
      setImages(mappedImages);
      setCourseName(data.courseName);
      
      if (!courseData?.fileId) {
        setCourseData({
          fileId: id,
          courseName: data.courseName,
        });
      }
    } catch (error) {
      console.error("Fetch error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch images",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFetch = () => {
    if (!fileId.trim()) {
      toast({ title: "Error", description: "Please enter a File ID", variant: "destructive" });
      return;
    }
    fetchImages(fileId, videoNumber);
  };

  const handleRegenerate = async (videoNumber: number, imageIndex: number) => {
    const key = `${videoNumber}-${imageIndex}`;
    setRegeneratingIndex(key);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/regenerate-image/${fileId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ videoNumber, imageIndex }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to regenerate image");
      }

      const data = await response.json();
      
      setImages((prev) =>
        prev.map((img) =>
          img.videoNumber === videoNumber && img.imageIndex === imageIndex
            ? { ...img, imageUrl: data.imageUrl }
            : img
        )
      );

      toast({ title: "Success", description: "Image regenerated!" });
    } catch (error) {
      console.error("Regenerate error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to regenerate image",
        variant: "destructive",
      });
    } finally {
      setRegeneratingIndex(null);
    }
  };

  const handleCopyUrl = async (url: string) => {
    await navigator.clipboard.writeText(url);
    setCopiedUrl(url);
    toast({ title: "Copied!", description: "Image URL copied to clipboard" });
    setTimeout(() => setCopiedUrl(null), 2000);
  };

  // Group images by video number
  const groupedImages = images.reduce((acc, img) => {
    if (!acc[img.videoNumber]) {
      acc[img.videoNumber] = [];
    }
    acc[img.videoNumber].push(img);
    return acc;
  }, {} as Record<number, ImageData[]>);

  return (
    <PageTransition>
      <div className="container mx-auto px-6 max-w-6xl">
        <StepIndicator />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-10"
        >
          <h1 className="text-4xl font-bold mb-3">
            Storyboard <span className="gradient-text">Frames</span>
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            View and manage generated storyboard images for each video in your course.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6 mb-8"
        >
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1 space-y-2">
              <Label htmlFor="fileId">File ID</Label>
              <Input
                id="fileId"
                placeholder="Enter course file ID..."
                value={fileId}
                onChange={(e) => setFileId(e.target.value)}
              />
            </div>
            <div className="w-full sm:w-32 space-y-2">
              <Label htmlFor="videoNumber">Video # (optional)</Label>
              <Input
                id="videoNumber"
                type="number"
                min="1"
                placeholder="All"
                value={videoNumber}
                onChange={(e) => setVideoNumber(e.target.value)}
              />
            </div>
            <Button onClick={handleFetch} disabled={isLoading}>
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Fetch Frames
            </Button>
          </div>
          {courseName && (
            <p className="mt-4 text-sm text-muted-foreground">
              Course: <span className="font-medium text-foreground">{courseName}</span>
            </p>
          )}
        </motion.div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Loading storyboard frames...</p>
          </div>
        ) : images.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-card p-12 text-center"
          >
            <Grid3X3 className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">No Frames Yet</h3>
            <p className="text-muted-foreground">
              Enter a File ID and click "Fetch Frames" to view storyboard images.
            </p>
          </motion.div>
        ) : (
          <AnimatePresence mode="wait">
            <motion.div
              key="images-grid"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-10"
            >
              {Object.entries(groupedImages).map(([videoNum, videoImages], groupIndex) => (
                <motion.div
                  key={videoNum}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: groupIndex * 0.1 }}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <ImageIcon className="w-5 h-5 text-primary" />
                    </div>
                    <h2 className="text-xl font-semibold">Video {videoNum}</h2>
                    <span className="text-sm text-muted-foreground">
                      {videoImages.length} frames
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                    {videoImages.map((img, idx) => {
                      const key = `${img.videoNumber}-${img.imageIndex}`;
                      const isRegenerating = regeneratingIndex === key;
                      const isCopied = copiedUrl === img.imageUrl;

                      return (
                        <motion.div
                          key={key}
                          initial={{ opacity: 0, scale: 0.95 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: idx * 0.05 }}
                          className="group glass-card overflow-hidden"
                        >
                          <div className="aspect-video relative overflow-hidden bg-muted">
                            {isRegenerating ? (
                              <div className="absolute inset-0 flex items-center justify-center bg-background/80">
                                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                              </div>
                            ) : (
                              <img
                                src={img.imageUrl}
                                alt={`Video ${img.videoNumber} Frame ${img.imageIndex}`}
                                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                              />
                            )}
                          </div>
                          <div className="p-3">
                            <p className="text-sm font-medium mb-2">
                              Frame {img.imageIndex}
                            </p>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                className="flex-1"
                                onClick={() => handleRegenerate(img.videoNumber, img.imageIndex)}
                                disabled={isRegenerating}
                              >
                                <RefreshCw className={`w-3 h-3 ${isRegenerating ? "animate-spin" : ""}`} />
                                Regenerate
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyUrl(img.imageUrl)}
                              >
                                {isCopied ? (
                                  <Check className="w-3 h-3 text-green-500" />
                                ) : (
                                  <Copy className="w-3 h-3" />
                                )}
                              </Button>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </AnimatePresence>
        )}

        {images.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex justify-between mt-10"
          >
            <Button variant="outline" onClick={() => navigate("/")}>
              <ArrowLeft className="w-4 h-4" />
              Back to Upload
            </Button>
            <Button variant="gradient" onClick={() => navigate("/frames")}>
              Final Frame Selection
              <ArrowRight className="w-4 h-4" />
            </Button>
          </motion.div>
        )}
      </div>
    </PageTransition>
  );
}
