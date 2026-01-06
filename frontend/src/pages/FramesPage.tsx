import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  ArrowLeft, Loader2, CheckCircle2, Film, 
  Sparkles, AlertCircle, Images, Copy, Check, PanelRightClose, PanelRightOpen,
  Play, Download
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useStore } from "@/lib/store";
import { PageTransition } from "@/components/layout/PageTransition";
import { StepIndicator } from "@/components/layout/StepIndicator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/hooks/use-toast";
import { ScrollArea } from "@/components/ui/scroll-area";

interface VideoSelection {
  videoNumber: number;
  firstFrameUrl: string;
  thirdFrameUrl: string;
  promptEdit: string;
}

interface StoryboardImage {
  id: string;
  video_number: number;
  image_index: number;
  image_url: string;
}

export default function FramesPage() {
  const navigate = useNavigate();
  const { courseData } = useStore();
  const [fileId, setFileId] = useState(courseData?.fileId || "");
  const [courseName, setCourseName] = useState(courseData?.courseName || "");
  const [baseAvatarPrompt, setBaseAvatarPrompt] = useState(courseData?.baseAvatarPrompt || "");
  const [baseStoryboardPrompt, setBaseStoryboardPrompt] = useState(courseData?.baseStoryboardPrompt || "");
  const [videos, setVideos] = useState<VideoSelection[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [storyboardImages, setStoryboardImages] = useState<StoryboardImage[]>([]);
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(true);

  useEffect(() => {
    if (courseData?.fileId && !hasLoaded) {
      fetchFrames(courseData.fileId);
    }
  }, [courseData?.fileId]);

  const fetchImages = async (id: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/get-images/${id}`
      );
      const data = await response.json();
      if (response.ok) {
        setStoryboardImages(data.images || []);
      }
    } catch (error) {
      console.error("Failed to fetch storyboard images:", error);
    }
  };

  const fetchFrames = async (id: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/frames/${id}`
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to fetch frames");
      }

      const data = await response.json();
      setCourseName(data.courseName);
      setBaseAvatarPrompt(data.baseAvatarPrompt || "");
      setBaseStoryboardPrompt(data.baseStoryboardPrompt || "");
      
      // Initialize videos array - either from saved data or create empty ones
      if (data.videos && data.videos.length > 0) {
        setVideos(data.videos.map((v: any) => ({
          videoNumber: v.video_number,
          firstFrameUrl: v.first_frame_url || "",
          thirdFrameUrl: v.third_frame_url || "",
          promptEdit: v.prompt_edit || "",
        })));
      } else {
        // Create default 3 videos for selection
        setVideos([1, 2, 3].map((num) => ({
          videoNumber: num,
          firstFrameUrl: "",
          thirdFrameUrl: "",
          promptEdit: "",
        })));
      }
      
      // Also fetch storyboard images
      fetchImages(id);
      
      setHasLoaded(true);
    } catch (error) {
      console.error("Fetch error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch frames",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (url: string) => {
    navigator.clipboard.writeText(url);
    setCopiedUrl(url);
    setTimeout(() => setCopiedUrl(null), 2000);
  };

  const handleFetch = () => {
    if (!fileId.trim()) {
      toast({ title: "Error", description: "Please enter a File ID", variant: "destructive" });
      return;
    }
    fetchFrames(fileId);
  };

  const updateVideo = (videoNumber: number, field: keyof VideoSelection, value: string) => {
    setVideos((prev) =>
      prev.map((v) =>
        v.videoNumber === videoNumber ? { ...v, [field]: value } : v
      )
    );
  };

  const handleSave = async () => {
    if (!fileId.trim()) {
      toast({ title: "Error", description: "File ID is required", variant: "destructive" });
      return;
    }

    setIsSaving(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/frames/${fileId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ videos }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to save frames");
      }

      toast({ 
        title: "Success", 
        description: "Frame selections saved successfully!",
      });
    } catch (error) {
      console.error("Save error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to save frames",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <PageTransition>
      <div className="flex min-h-screen">
        {/* Main Content */}
        <div 
          className={`flex-1 transition-all duration-300 ${
            isPanelOpen && hasLoaded && storyboardImages.length > 0 ? "mr-[400px]" : ""
          }`}
        >
          <div className="container mx-auto px-6 max-w-5xl">
            <StepIndicator />

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-center mb-10"
            >
              <h1 className="text-4xl font-bold mb-3">
                Final Frame <span className="gradient-text">Selection</span>
              </h1>
              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Choose the key storyboard frames for each video and add custom prompt refinements.
              </p>
            </motion.div>

            {/* File ID Input */}
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
                <Button onClick={handleFetch} disabled={isLoading}>
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4" />
                  )}
                  Load Course
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
                <p className="text-muted-foreground">Loading course data...</p>
              </div>
            ) : hasLoaded ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-8"
              >
                {/* Base Prompts */}
                <div className="glass-card p-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold">Base Prompts</h2>
                      <p className="text-sm text-muted-foreground">Read-only prompts generated for this course</p>
                    </div>
                  </div>

                  <div className="grid gap-6 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Base Avatar Prompt</Label>
                      <Textarea
                        value={baseAvatarPrompt}
                        readOnly
                        className="min-h-[120px] bg-muted/50 resize-none"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Base Storyboard Prompt</Label>
                      <Textarea
                        value={baseStoryboardPrompt}
                        readOnly
                        className="min-h-[120px] bg-muted/50 resize-none"
                      />
                    </div>
                  </div>
                </div>

                {/* Video Frame Selections */}
                <div className="space-y-6">
                  {videos.map((video, index) => (
                    <motion.div
                      key={video.videoNumber}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="glass-card p-6"
                    >
                      <div className="flex items-center gap-3 mb-6">
                        <div className="h-10 w-10 rounded-lg bg-accent/10 flex items-center justify-center">
                          <Film className="w-5 h-5 text-accent" />
                        </div>
                        <h3 className="text-lg font-semibold">Video {video.videoNumber}</h3>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2 mb-4">
                        <div className="space-y-2">
                          <Label>First Frame URL</Label>
                          <Input
                            placeholder="Opening moment URL..."
                            value={video.firstFrameUrl}
                            onChange={(e) => updateVideo(video.videoNumber, "firstFrameUrl", e.target.value)}
                          />
                          {video.firstFrameUrl && (
                            <img
                              src={video.firstFrameUrl}
                              alt="First frame"
                              className="w-full aspect-video object-cover rounded-lg mt-2"
                            />
                          )}
                        </div>
                        <div className="space-y-2">
                          <Label>Last Frame URL</Label>
                          <Input
                            placeholder="Closing moment URL..."
                            value={video.thirdFrameUrl}
                            onChange={(e) => updateVideo(video.videoNumber, "thirdFrameUrl", e.target.value)}
                          />
                          {video.thirdFrameUrl && (
                            <img
                              src={video.thirdFrameUrl}
                              alt="Last frame"
                              className="w-full aspect-video object-cover rounded-lg mt-2"
                            />
                          )}
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Prompt Edit</Label>
                        <Textarea
                          placeholder="Add visual refinements, e.g., 'Warmer lighting, avatar more energetic, closer camera angle...'"
                          value={video.promptEdit}
                          onChange={(e) => updateVideo(video.videoNumber, "promptEdit", e.target.value)}
                          className="min-h-[80px]"
                        />
                      </div>

                      <div className="flex gap-3 mt-4 pt-4 border-t border-border">
                        <Button className="flex-1">
                          <Play className="w-4 h-4" />
                          Generate
                        </Button>
                        <Button variant="outline" className="flex-1">
                          <Download className="w-4 h-4" />
                          Download
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Back Button */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <Button variant="outline" onClick={() => navigate("/images")}>
                    <ArrowLeft className="w-4 h-4" />
                    Back to Images
                  </Button>
                </motion.div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass-card p-12 text-center"
              >
                <AlertCircle className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-xl font-semibold mb-2">No Course Loaded</h3>
                <p className="text-muted-foreground">
                  Enter a File ID and click "Load Course" to start selecting frames.
                </p>
              </motion.div>
            )}
          </div>
        </div>

        {/* Fixed Right Panel */}
        {hasLoaded && storyboardImages.length > 0 && (
          <>
            {/* Toggle Button */}
            <Button
              variant="outline"
              size="icon"
              className={`fixed top-24 z-50 transition-all duration-300 ${
                isPanelOpen ? "right-[412px]" : "right-4"
              }`}
              onClick={() => setIsPanelOpen(!isPanelOpen)}
            >
              {isPanelOpen ? (
                <PanelRightClose className="w-4 h-4" />
              ) : (
                <PanelRightOpen className="w-4 h-4" />
              )}
            </Button>

            {/* Side Panel */}
            <div
              className={`fixed top-0 right-0 h-full w-[400px] bg-background border-l border-border transition-transform duration-300 z-40 ${
                isPanelOpen ? "translate-x-0" : "translate-x-full"
              }`}
            >
              <div className="p-4 border-b border-border">
                <div className="flex items-center gap-2">
                  <Images className="w-5 h-5 text-primary" />
                  <h2 className="text-lg font-semibold">Storyboard Images</h2>
                  <span className="text-sm text-muted-foreground">({storyboardImages.length})</span>
                </div>
              </div>
              <ScrollArea className="h-[calc(100vh-65px)]">
                <div className="p-4 space-y-4">
                  {storyboardImages.map((img) => (
                    <div key={img.id} className="border rounded-lg p-3 space-y-2">
                      <p className="text-sm font-medium">
                        Video {img.video_number} - Frame {img.image_index}
                      </p>
                      <img
                        src={img.image_url}
                        alt={`Video ${img.video_number} Frame ${img.image_index}`}
                        className="w-full aspect-video object-cover rounded"
                      />
                      <Button
                        size="sm"
                        variant="outline"
                        className="w-full"
                        onClick={() => copyToClipboard(img.image_url)}
                      >
                        {copiedUrl === img.image_url ? (
                          <>
                            <Check className="w-4 h-4 text-green-500" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" />
                            Copy URL
                          </>
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          </>
        )}
      </div>
    </PageTransition>
  );
}
