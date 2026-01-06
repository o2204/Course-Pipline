import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Loader2, Sparkles } from 'lucide-react';
// import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/services/api';

export default function UploadPage() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [courseName, setCourseName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validExtensions = ['.pdf', '.docx', '.doc'];
      const fileExt = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();

      if (!validExtensions.includes(fileExt)) {
        toast({
          title: 'Invalid File Type',
          description: 'Please upload a .pdf, .docx, or .doc file',
          variant: 'destructive',
        });
        return;
      }

      setFile(selectedFile);
      // Auto-extract course name if empty
      if (!courseName) {
        setCourseName(selectedFile.name.replace(/\.[^/.]+$/, "").replace(/\s+/g, '_').toLowerCase());
      }
    }
  };

  const handleUpload = async () => {
    if (!courseName.trim() || !file) return;

    try {
      setIsUploading(true);

      // 1. Upload File
      await apiClient.uploadFile(courseName, file);

      // 2. Generate Prompts (Backend trigger)
      await apiClient.generatePrompts(courseName);

      toast({
        title: 'Success',
        description: 'Course initialized successfully',
      });

      // Navigate to Page 2
      navigate(`/generate-images/${courseName}`);

    } catch (error) {
      console.error('Error:', error);
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'An error occurred',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-[128px]" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/20 rounded-full blur-[128px]" />

      <div className="glass-card w-full max-w-xl p-8 z-10">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-primary/10 mb-4">
            <Sparkles className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">
            Create <span className="text-gradient">Storyboard</span>
          </h1>
          <p className="text-muted-foreground">
            Upload your course document to begin the visual generation process.
          </p>
        </div>

        <div className="space-y-8">
          {/* File Drop Area */}
          <div className="relative group">
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.docx,.doc"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20 disabled:cursor-as-waiting"
              disabled={isUploading}
            />
            <div className={`
              border-2 border-dashed rounded-xl p-10 text-center transition-all duration-300
              ${file ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-muted/50'}
            `}>
              {file ? (
                <div className="flex flex-col items-center">
                  <FileText className="w-10 h-10 text-primary mb-3" />
                  <p className="font-medium text-lg">{file.name}</p>
                  <p className="text-sm text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              ) : (
                <div className="flex flex-col items-center text-muted-foreground">
                  <Upload className="w-10 h-10 mb-3 group-hover:text-primary transition-colors" />
                  <p className="font-medium">Click or drag a file here</p>
                  <p className="text-sm mt-1">PDF, DOCX, or DOC</p>
                </div>
              )}
            </div>
          </div>

          {/* Course Name */}
          <div className="space-y-2">
            <Label htmlFor="courseName">Course Name</Label>
            <Input
              id="courseName"
              placeholder="course_name_v1"
              value={courseName}
              onChange={(e) => setCourseName(e.target.value)}
              disabled={isUploading}
              className="bg-background/50"
            />
            <p className="text-xs text-muted-foreground">
              This will be used as the unique identifier for your project.
            </p>
          </div>

          {/* CTA */}
          <button
            onClick={handleUpload}
            disabled={!courseName.trim() || !file || isUploading}
            className="text-white font-normal w-full cursor-pointer h-12 text-lg bg-aurora rounded-md
            dark:bg-gradient-to-br 
            dark:from-purple-500 
            dark:via-purple-500 
            dark:to-cyan-500
            hover:bg-red-500
            "
          >
            {isUploading ? (
              <div className='flex items-center gap-2 justify-center '>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Processing...
              </div>
            ) : (
              "Create Storyboard"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
