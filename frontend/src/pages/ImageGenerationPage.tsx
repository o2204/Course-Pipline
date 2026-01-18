import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ChevronDown, ChevronUp, Image as ImageIcon,
  Download, Loader2, Sparkles, AlertCircle, CheckCircle2,
  RotateCw
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { Button } from '@/components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { apiClient, StoryboardJSON, Video, Shot, Frame, BulkImageStatus } from '@/services/api';

export default function ImageGenerationPage() {
  const { courseName } = useParams<{ courseName: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [storyboard, setStoryboard] = useState<StoryboardJSON | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // State for generated images: key format "V{v}_S{s}_F{f}" -> url
  const [generatedImages, setGeneratedImages] = useState<Record<string, string>>({});

  // Track generating states
  const [generatingFrame, setGeneratingFrame] = useState<string | null>(null);
  const [generatingVideo, setGeneratingVideo] = useState<number | null>(null);
  const [generatingAll, setGeneratingAll] = useState(false);

  // Track expanded prompts: key "V{v}_S{s}_F{f}"
  const [expandedPrompts, setExpandedPrompts] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (courseName) {
      loadStoryboard();
    }
  }, [courseName]);

  const loadStoryboard = async () => {
    if (!courseName) return;
    try {
      setIsLoading(true);
      const data = await apiClient.getPrompts(courseName);
      setStoryboard(data.prompt_json);

      // Ideally we would also fetch existing generated images here
      // But for now we start empty or could add an API endpoint to fetch state
    } catch (error) {
      console.error('Failed to load storyboard:', error);
      toast({
        title: 'Error',
        description: 'Failed to load storyboard configuration.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getFrameId = (v: number, s: number, f: number) => `V${v}_S${s}_F${f}`;

  const togglePrompt = (id: string) => {
    setExpandedPrompts(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleGenerateFrame = async (v: number, s: number, f: number) => {
    if (!courseName) return;
    const frameCode = getFrameId(v, s, f);

    try {
      setGeneratingFrame(frameCode);
      const res = await apiClient.generateImage(courseName, frameCode);

      setGeneratedImages(prev => ({
        ...prev,
        [frameCode]: res.image_url
      }));

      toast({ title: 'Image Generated', description: `Frame ${frameCode} ready.` });
    } catch (error) {
      toast({
        title: 'Generation Failed',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive'
      });
    } finally {
      setGeneratingFrame(null);
    }
  };

  const handleGenerateVideoImages = async (videoNumber: number) => {
    if (!courseName) return;

    try {
      setGeneratingVideo(videoNumber);
      const res = await apiClient.generateBulkImages(courseName, videoNumber);

      // Update local state with new images
      const newImages: Record<string, string> = {};
      res.images.forEach((item: BulkImageStatus) => {
        if (item.status === 'success' && item.image_url) {
          // Map backend frame_code (likely same format) to our key
          // Assuming backend returns "V1_S1_F1" matching our helper
          newImages[item.frame_code] = item.image_url;
        }
      });

      setGeneratedImages(prev => ({ ...prev, ...newImages }));

      toast({
        title: 'Bulk Generation Complete',
        description: `Generated ${res.generated} images. ${res.failed} failed.`
      });

    } catch (error) {
      toast({
        title: 'Bulk Generation Failed',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive'
      });
    } finally {
      setGeneratingVideo(null);
    }
  };

  const handleDownload = async (url: string, filename: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      console.error(e);
      toast({ title: 'Download failed', variant: 'destructive' });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!storyboard) return <div className="p-8 text-center">No storyboard found.</div>;

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-5xl mx-auto space-y-8">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Image <span className="text-gradient">Generation</span></h1>
            <p className="text-muted-foreground mt-1">Generate and refine frames for {courseName}</p>
          </div>
          <Button
            onClick={() => navigate(`/generate-video/${courseName}`)}
            className="group"
          >
            Next: Video Generation
            <CheckCircle2 className="ml-2 w-4 h-4 group-hover:text-green-400 transition-colors mt-32" />
          </Button>
        </div>

        {/* Videos Accordion */}
        <Accordion type="single" collapsible className="space-y-4" defaultValue={`video-${storyboard.videos[0]?.video_number}`}>
          {storyboard.videos.map((video: Video) => (
            <AccordionItem
              key={video.video_number}
              value={`video-${video.video_number}`}
              className="glass-card border-none px-4"
            >
              <AccordionTrigger className="hover:no-underline py-4">
                <div className="flex items-center gap-4 w-full">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                    {video.video_number}
                  </span>
                  <div className="flex-1 text-left">
                    <h3 className="font-semibold text-lg">Video Sequence {video.video_number}</h3>
                    <p className="text-sm text-muted-foreground">
                      {video.shots.length} shots • {video.shots.reduce((a, s) => a + s.frames.length, 0)} frames
                    </p>
                  </div>
                  {/* Stop bubbling to prevent accordion toggle when clicking button */}
                  <div onClick={(e) => e.stopPropagation()} className="mr-4">
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={generatingVideo === video.video_number}
                      onClick={() => handleGenerateVideoImages(video.video_number)}
                    >
                      {generatingVideo === video.video_number ? (
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      ) : (
                        <Sparkles className="w-4 h-4 mr-2" />
                      )}
                      Generate All Images
                    </Button>
                  </div>
                </div>
              </AccordionTrigger>

              <AccordionContent className="pt-2 pb-6 space-y-8">
                {video.shots.map((shot: Shot) => (
                  <div key={shot.shot_number} className="relative pl-6 border-l-2 border-primary/20">
                    <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-primary/20 border-2 border-background" />
                    <h4 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wider">
                      Shot {shot.shot_number} • {shot.scene_en}
                    </h4>

                    <div className="grid gap-4">
                      {shot.frames.map((frame: Frame) => {
                        const frameId = getFrameId(video.video_number, shot.shot_number, frame.frame_number);
                        const isExpanded = expandedPrompts.has(frameId);
                        const imageUrl = generatedImages[frameId];
                        const isGenerating = generatingFrame === frameId;

                        return (
                          <div key={frame.frame_number} className="group bg-card/30 rounded-xl p-4 border border-white/5 hover:border-white/10 transition-colors">
                            <div className="flex items-start gap-4">

                              {/* Left: Controls & Info */}
                              <div className="flex-1 space-y-3">
                                <div className="flex items-center gap-3">
                                  <Badge variant="outline" className="bg-primary/5 border-primary/20">
                                    {frameId}
                                  </Badge>
                                  <button
                                    onClick={() => togglePrompt(frameId)}
                                    className="text-xs font-medium text-primary hover:underline flex items-center gap-1 transition-colors"
                                  >
                                    {isExpanded ? 'Hide Prompt' : 'Show Prompt'}
                                    {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                  </button>
                                </div>

                                <AnimatePresence>
                                  {isExpanded && (
                                    <motion.div
                                      initial={{ height: 0, opacity: 0 }}
                                      animate={{ height: 'auto', opacity: 1 }}
                                      exit={{ height: 0, opacity: 0 }}
                                      className="overflow-hidden"
                                    >
                                      <p className="text-sm text-foreground/80 leading-relaxed bg-black/20 p-3 rounded-lg border border-white/5">
                                        {frame.frame_prompt}
                                      </p>
                                    </motion.div>
                                  )}
                                </AnimatePresence>

                                {/* Action Bar */}
                                <div className="flex items-center gap-2 pt-2">
                                  <Button
                                    size="sm"
                                    onClick={() => handleGenerateFrame(video.video_number, shot.shot_number, frame.frame_number)}
                                    disabled={isGenerating}
                                    className={imageUrl ? "bg-secondary/20 hover:bg-secondary/30 text-secondary-foreground" : ""}
                                  >
                                    {isGenerating ? (
                                      <>
                                        <Loader2 className="w-3 h-3 animate-spin mr-2" />
                                        Generating...
                                      </>
                                    ) : imageUrl ? (
                                      <>
                                        <RotateCw className="w-3 h-3 text-black" />
                                      </>
                                    ) : (
                                      <>
                                        <Sparkles className="w-3 h-3 mr-2" />
                                        Generate Image
                                      </>
                                    )}
                                  </Button>

                                  {imageUrl && (
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => handleDownload(imageUrl, `${frameId}.png`)}
                                    >
                                      <Download className="w-3 h-3" />
                                    </Button>
                                  )}
                                </div>
                              </div>

                              {/* Right: Image Preview */}
                              <div 
                                className="w-48 aspect-video bg-black/40 rounded-lg border border-white/10 overflow-hidden flex items-center justify-center relative cursor-pointer hover:border-primary/50 transition-all"
                                onClick={() => {
                                  if (imageUrl) {
                                    navigator.clipboard.writeText(imageUrl);
                                    toast({
                                      title: 'Copied',
                                      description: 'Image URL copied to clipboard'
                                    });
                                  }
                                }}
                                title={imageUrl ? "Click to copy image URL" : undefined}
                              >
                                {imageUrl ? (
                                  <motion.img
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    src={imageUrl}
                                    alt={frameId}
                                    className="w-full h-full object-cover"
                                  />
                                ) : (
                                  <ImageIcon className="w-8 h-8 text-muted-foreground/30" />
                                )}
                              </div>

                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </div>
  );
}
