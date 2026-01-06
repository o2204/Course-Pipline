-- Create course_files table
CREATE TABLE public.course_files (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  course_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  base_avatar_prompt TEXT,
  base_storyboard_prompt TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create video_images table
CREATE TABLE public.video_images (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  course_file_id UUID NOT NULL REFERENCES public.course_files(id) ON DELETE CASCADE,
  video_number INTEGER NOT NULL,
  image_index INTEGER NOT NULL,
  image_url TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create video_frame_selections table
CREATE TABLE public.video_frame_selections (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  course_file_id UUID NOT NULL REFERENCES public.course_files(id) ON DELETE CASCADE,
  video_number INTEGER NOT NULL,
  first_frame_url TEXT,
  middle_frame_url TEXT,
  third_frame_url TEXT,
  prompt_edit TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS on all tables (public access for internal tool)
ALTER TABLE public.course_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.video_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.video_frame_selections ENABLE ROW LEVEL SECURITY;

-- Create public access policies (internal tool - no auth required)
CREATE POLICY "Allow public access to course_files" ON public.course_files FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to video_images" ON public.video_images FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public access to video_frame_selections" ON public.video_frame_selections FOR ALL USING (true) WITH CHECK (true);

-- Create indexes for performance
CREATE INDEX idx_video_images_course_file ON public.video_images(course_file_id);
CREATE INDEX idx_video_images_video_number ON public.video_images(course_file_id, video_number);
CREATE INDEX idx_video_frame_selections_course_file ON public.video_frame_selections(course_file_id);

-- Create function to auto-update updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for video_frame_selections
CREATE TRIGGER update_video_frame_selections_updated_at
  BEFORE UPDATE ON public.video_frame_selections
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create storage bucket for course files
INSERT INTO storage.buckets (id, name, public) VALUES ('course-files', 'course-files', true);

-- Storage policies for course files bucket
CREATE POLICY "Allow public read access" ON storage.objects FOR SELECT USING (bucket_id = 'course-files');
CREATE POLICY "Allow public upload" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'course-files');
CREATE POLICY "Allow public update" ON storage.objects FOR UPDATE USING (bucket_id = 'course-files');
CREATE POLICY "Allow public delete" ON storage.objects FOR DELETE USING (bucket_id = 'course-files');