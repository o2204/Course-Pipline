import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Play, Download, Loader2, Video as VideoIcon,
  Copy, Image as ImageIcon, ChevronsRight
} from 'lucide-react';
import { motion } from 'framer-motion';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { apiClient, StoryboardJSON, Video, Frame, Shot } from '@/services/api';


export default function VideoGenerationPage() {
  const { courseName } = useParams<{ courseName: string }>();
  const { toast } = useToast();

  const [storyboard, setStoryboard] = useState<StoryboardJSON | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Form State
  const [firstFrameUrl, setFirstFrameUrl] = useState('');
  const [lastFrameUrl, setLastFrameUrl] = useState('');
  const [motionPrompt, setMotionPrompt] = useState('');

  // Generation State
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null);

  const [images, setImages] = useState<any[]>([]);

  const loadImages = async () => {
    if (!courseName) return;
    try {
      const data = await apiClient.getImages(courseName);
      setImages(data.images);
    } catch (error) {
      console.error("Failed to load images:", error);
    }
  };

  const loadData = async () => {
    if (!courseName) return;
    try {
      setIsLoading(true);
      const [promptData, imageData] = await Promise.all([
        apiClient.getPrompts(courseName),
        apiClient.getImages(courseName)
      ]);

      setStoryboard(promptData.prompt_json);
      setImages(imageData.images);

      // Default to first video
      if (promptData.prompt_json && promptData.prompt_json.videos.length > 0) {
        setSelectedVideo(promptData.prompt_json.videos[0]);
      }
    } catch (error) {
      console.error(error);
      toast({ title: 'Error', description: 'Failed to load data', variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (courseName) {
      loadData();
    }
  }, [courseName]);

  const handleVideoSelect = (video: Video) => {
    setSelectedVideo(video);
    setGeneratedVideoUrl(null);
    // Clear inputs when switching video to avoid confusion, or keep them if intended
    setFirstFrameUrl('');
    setLastFrameUrl('');
    setMotionPrompt('');
  };

  const handleCopyUrl = (url: string) => {
    if (!url) return;
    navigator.clipboard.writeText(url);
    toast({ title: 'Copied', description: 'URL copied to clipboard' });
  };

  const handleGenerate = async () => {
    if (!courseName || !selectedVideo) return;

    if (!firstFrameUrl.trim()) {
      toast({
        title: 'Input Required',
        description: 'First Frame URL (url_1) is required for video generation.',
        variant: 'destructive'
      });
      return;
    }

    try {
      setIsGenerating(true);
      const res = await apiClient.generateVideo(
        courseName,
        selectedVideo.video_number,
        firstFrameUrl,
        lastFrameUrl || undefined,
        motionPrompt || undefined
      );

      setGeneratedVideoUrl(res.video_url);

      // Refresh images state as per requirements
      await loadImages();

      toast({ title: 'Success', description: 'Video generated successfully' });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Video generation failed',
        variant: 'destructive'
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadVideo = async (url: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `video_${selectedVideo?.video_number || 'output'}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Download failed:', error);
      toast({
        title: 'Download Failed',
        description: 'Could not download video. Please try opening in a new tab.',
        variant: 'destructive'
      });
    }
  };

  if (isLoading) return <div className="flex justify-center p-20"><Loader2 className="animate-spin" /></div>;
  if (!storyboard) return <div>No data</div>;

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar: Video Selector & Frame References */}
      <div className="w-80 border-r border-border bg-card/20 flex flex-col h-screen sticky top-0">

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="text-xs font-medium text-muted-foreground uppercase tracking-widest mb-4">
            Generated Images
          </div>

          {/* Display all images vertically */}
          {images.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <ImageIcon className="w-12 h-12 mb-3 opacity-30" />
              <p className="text-sm">No images generated yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {images.map((image, index) => (
                <div
                  key={image.frame_code || index}
                  className="group relative aspect-video bg-black/40 rounded border border-white/10 overflow-hidden cursor-pointer hover:border-primary/50 transition-all"
                  onClick={() => {
                    navigator.clipboard.writeText(image.image_url);
                    toast({
                      title: 'Copied',
                      description: 'Image URL copied'
                    });
                  }}
                  title="Click to copy image URL"
                >
                  <img
                    src={image.image_url}
                    alt={image.frame_code || `Image ${index + 1}`}
                    className="w-full h-full object-contain"
                  />
                  {/* Copy icon overlay on hover */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center">
                    <Copy className="w-6 h-6 opacity-0 group-hover:opacity-100 transition-opacity text-white" />
                  </div>
                  {/* Frame code label */}
                  <div className="absolute bottom-0 left-0 right-0 bg-black/60 backdrop-blur-sm px-2 py-1 text-[10px] text-white/80 font-mono">
                    {image.frame_code}
                  </div>
                </div>
              ))}
            </div>
          )}

        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1  p-8 overflow-y-auto h-screen">
        <div className="max-w-4xl mx-auto space-y-8">
          <div>
            <h1 className="text-3xl font-bold">Video <span className="text-gradient">Generation</span></h1>
            <p className="text-md text-muted-foreground mt-2">
              Compose and generate Video {selectedVideo?.video_number}
            </p>
          </div>
          <div className="space-y-6">
            <div className="glass-card p-1 overflow-hidden rounded-xl bg-black/60 shadow-2xl">
              {generatedVideoUrl ? (
                <video
                  controls
                  className="w-full aspect-video object-contain"
                  src={generatedVideoUrl}
                />
              ) : (
                <div className="w-full aspect-video flex flex-col items-center justify-center text-muted-foreground">
                  <VideoIcon className="w-16 h-16 mb-4 opacity-30" />
                  <p className="text-sm">Video Preview</p>
                </div>
              )}
            </div>

            {generatedVideoUrl && (
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  onClick={() => handleDownloadVideo(generatedVideoUrl)}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Video
                </Button>
              </div>
            )}
          </div>

          {/* Left: Inputs */}
          <div className="space-y-6 glass-card p-6">
            <h3 className="font-semibold flex items-center gap-2">
              <ChevronsRight className="w-4 h-4 text-primary" />
              Input Parameters
            </h3>

            <div className="space-y-3">
              <Label>
                First Frame URL
                <span className="text-red-500 ml-1.5 text-xs font-normal">required</span>
              </Label>
              <div className="flex gap-2">
                <Input
                  placeholder="https://..."
                  value={firstFrameUrl}
                  onChange={e => setFirstFrameUrl(e.target.value)}
                />
                <Button size="icon" variant="ghost" onClick={() => handleCopyUrl(firstFrameUrl)}>
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>0OBSERVED

            <div className="space-y-3">
              <Label>
                Last Frame URL
                <span className="text-muted-foreground ml-1.5 text-xs font-normal">optional</span>
              </Label>
              <div className="flex gap-2">
                <Input
                  placeholder="https://..."
                  value={lastFrameUrl}
                  onChange={e => setLastFrameUrl(e.target.value)}
                />
                <Button size="icon" variant="ghost" onClick={() => handleCopyUrl(lastFrameUrl)}>
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-3">
              <Label>
                Motion Prompt
                <span className="text-muted-foreground ml-1.5 text-xs font-normal">optional</span>
              </Label>
              <Textarea
                placeholder="Describe the camera movement and action..."
                className="min-h-[120px] resize-none"
                value={motionPrompt}
                onChange={e => setMotionPrompt(e.target.value)}
              />
            </div>

            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !selectedVideo}
              className="text-white hover:text-white w-full h-12 text-lg bg-aurora"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Generating Video...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  Generate Video
                </>
              )}
            </Button>
          </div>

        </div>
      </div>
    </div>
  );
}
