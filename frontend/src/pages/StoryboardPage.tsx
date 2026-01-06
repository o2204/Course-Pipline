// Storyboard Page for Course Visual Generation Platform

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Loader2, Image as ImageIcon, Video, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { apiClient, StoryboardJSON, Video as VideoType, Shot, Frame } from '@/services/api';

export default function StoryboardPage() {
  const { courseName } = useParams<{ courseName: string }>();
  const { toast } = useToast();

  const [storyboard, setStoryboard] = useState<StoryboardJSON | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [generatingImages, setGeneratingImages] = useState<Set<string>>(new Set());
  const [generatingSingleImage, setGeneratingSingleImage] = useState<string | null>(null);
  const [generatingVideo, setGeneratingVideo] = useState<number | null>(null);
  const [generatedVideos, setGeneratedVideos] = useState<Record<number, { video_url: string, script_clean?: string }>>({});

  useEffect(() => {
    loadStoryboard();
  }, [courseName]);

  const loadStoryboard = async () => {
    if (!courseName) return;

    try {
      setIsLoading(true);
      const [promptData, videosData] = await Promise.all([
        apiClient.getPrompts(courseName),
        apiClient.getVideos(courseName).catch(() => []) // Handle error gracefully if no videos yet
      ]);
      setStoryboard(promptData.prompt_json);

      // Map videos to state
      const videoMap: Record<number, { video_url: string, script_clean?: string }> = {};
      videosData.forEach(v => {
        videoMap[v.video_number] = { video_url: v.video_url, script_clean: v.script_clean };
      });
      setGeneratedVideos(videoMap);

    } catch (error) {
      console.error('Error loading storyboard:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to load storyboard',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const generateFrameCode = (videoNum: number, shotNum: number, frameNum: number) => {
    return `V${videoNum}_S${shotNum}_F${frameNum}`;
  };

  const handleGenerateImage = async (videoNum: number, shotNum: number, frameNum: number) => {
    if (!courseName) return;

    const frameCode = generateFrameCode(videoNum, shotNum, frameNum);

    try {
      setGeneratingSingleImage(frameCode);
      const result = await apiClient.generateImage(courseName, frameCode);

      toast({
        title: 'Image Generated',
        description: result.message,
      });
    } catch (error) {
      console.error('Error generating image:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to generate image',
        variant: 'destructive',
      });
    } finally {
      setGeneratingSingleImage(null);
    }
  };

  const handleGenerateAllImages = async (videoNumber?: number) => {
    if (!courseName) return;

    const key = videoNumber ? `video-${videoNumber}` : 'all';
    setGeneratingImages(prev => new Set(prev).add(key));

    try {
      const result = await apiClient.generateBulkImages(courseName, videoNumber);

      toast({
        title: 'Bulk Generation Complete',
        description: `Generated ${result.generated} images, ${result.failed} failed`,
      });
    } catch (error) {
      console.error('Error generating bulk images:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to generate images',
        variant: 'destructive',
      });
    } finally {
      setGeneratingImages(prev => {
        const updated = new Set(prev);
        updated.delete(key);
        return updated;
      });
    }
  };

  const handleGenerateVideo = async (videoNumber: number) => {
    if (!courseName) return;

    try {
      setGeneratingVideo(videoNumber);
      const result = await apiClient.generateVideo(courseName, videoNumber);

      setGeneratedVideos(prev => ({
        ...prev,
        [videoNumber]: { video_url: result.video_url, script_clean: result.script_clean }
      }));

      toast({
        title: 'Video Generated',
        description: result.message,
      });
    } catch (error) {
      console.error('Error generating video:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to generate video',
        variant: 'destructive',
      });
    } finally {
      setGeneratingVideo(null);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4 flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading storyboard...</p>
        </div>
      </div>
    );
  }

  if (!storyboard) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card>
          <CardHeader>
            <CardTitle>Storyboard Not Found</CardTitle>
            <CardDescription>
              No storyboard found for course: {courseName}
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Storyboard: {courseName}</h1>
        <p className="text-muted-foreground">
          {storyboard.videos.length} video(s) •
          {storyboard.videos.reduce((acc, v) => acc + v.shots.length, 0)} shot(s) •
          {storyboard.videos.reduce((acc, v) => acc + v.shots.reduce((a, s) => a + s.frames.length, 0), 0)} frame(s)
        </p>
      </div>

      {/* Global Actions */}
      <div className="mb-6 flex gap-4">
        <Button
          onClick={() => handleGenerateAllImages()}
          disabled={generatingImages.has('all')}
        >
          {generatingImages.has('all') ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Generating All Images...
            </>
          ) : (
            <>
              <ImageIcon className="mr-2 h-4 w-4" />
              Generate All Images
            </>
          )}
        </Button>
      </div>

      {/* Videos */}
      <Accordion type="multiple" className="space-y-4">
        {storyboard.videos.map((video: VideoType) => (
          <AccordionItem key={video.video_number} value={`video-${video.video_number}`}>
            <Card>
              <AccordionTrigger className="px-6 hover:no-underline">
                <div className="flex items-center justify-between w-full pr-4">
                  <div className="flex items-center gap-3">
                    <Video className="h-5 w-5" />
                    <div className="text-left">
                      <h3 className="font-semibold">Video {video.video_number}</h3>
                      <p className="text-sm text-muted-foreground">
                        {video.shots.length} shots •
                        {video.shots.reduce((acc, s) => acc + s.frames.length, 0)} frames
                      </p>
                    </div>
                  </div>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <CardContent className="space-y-4 pt-4">
                  {/* Video Actions and Display */}
                  <div className="flex flex-col gap-4 pb-4 border-b">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleGenerateAllImages(video.video_number)}
                        disabled={generatingImages.has(`video-${video.video_number}`)}
                      >
                        {generatingImages.has(`video-${video.video_number}`) ? (
                          <>
                            <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                            Generating...
                          </>
                        ) : (
                          <>
                            <ImageIcon className="mr-2 h-3 w-3" />
                            Generate All Images for Video {video.video_number}
                          </>
                        )}
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => handleGenerateVideo(video.video_number)}
                        disabled={generatingVideo === video.video_number}
                      >
                        {generatingVideo === video.video_number ? (
                          <>
                            <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                            Generating Video...
                          </>
                        ) : (
                          <>
                            <Play className="mr-2 h-3 w-3" />
                            Generate Video {video.video_number}
                          </>
                        )}
                      </Button>
                    </div>

                    {/* Display Generated Video */}
                    {generatedVideos[video.video_number] && (
                      <div className="bg-muted p-4 rounded-lg">
                        <h4 className="font-medium mb-2 flex items-center gap-2">
                          <Video className="h-4 w-4" /> Generated Video
                        </h4>
                        <video controls className="w-full max-h-[400px] rounded-md bg-black">
                          <source src={generatedVideos[video.video_number].video_url} type="video/mp4" />
                          Your browser does not support the video tag.
                        </video>
                        {generatedVideos[video.video_number].script_clean && (
                          <div className="mt-2 text-sm text-muted-foreground p-2 bg-background rounded border">
                            <p className="font-semibold text-xs uppercase mb-1">Motion Prompt:</p>
                            {generatedVideos[video.video_number].script_clean}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Shots */}
                  {video.shots.map((shot: Shot) => (
                    <div key={shot.shot_number} className="pl-4 border-l-2">
                      <h4 className="font-medium mb-2 flex items-center gap-2">
                        <Badge variant="secondary">Shot {shot.shot_number}</Badge>
                        {shot.scene_en}
                      </h4>

                      {/* Frames */}
                      <div className="space-y-2 pl-4">
                        {shot.frames.map((frame: Frame) => {
                          const frameCode = generateFrameCode(video.video_number, shot.shot_number, frame.frame_number);
                          const isGenerating = generatingSingleImage === frameCode;

                          return (
                            <div
                              key={frame.frame_number}
                              className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg"
                            >
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <Badge variant="outline" className="text-xs">
                                    Frame {frame.frame_number}
                                  </Badge>
                                  <code className="text-xs text-muted-foreground">{frameCode}</code>
                                </div>
                                <p className="text-sm">{frame.frame_prompt}</p>
                              </div>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleGenerateImage(video.video_number, shot.shot_number, frame.frame_number)}
                                disabled={isGenerating}
                              >
                                {isGenerating ? (
                                  <Loader2 className="h-3 w-3 animate-spin" />
                                ) : (
                                  <ImageIcon className="h-3 w-3" />
                                )}
                              </Button>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </AccordionContent>
            </Card>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}
