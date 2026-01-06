// API Client for Course Visual Generation Platform

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ====================================================
// Types
// ====================================================

export interface UploadFileResponse {
  course_name: string;
  file_id: string;
  message: string;
}

export interface Frame {
  frame_number: number;
  frame_prompt: string;
}

export interface Shot {
  shot_number: number;
  scene_en: string;
  frames: Frame[];
}

export interface Video {
  video_number: number;
  shots: Shot[];
}

export interface StoryboardJSON {
  videos: Video[];
}

export interface GeneratePromptResponse {
  course_name: string;
  prompt_json: StoryboardJSON;
  model_name: string;
  success: boolean;
  message: string;
}

export interface GenerateImageResponse {
  course_name: string;
  frame_code: string;
  image_url: string;
  message: string;
}

export interface BulkImageStatus {
  frame_code: string;
  status: string;
  image_url?: string;
  error?: string;
}

export interface GenerateBulkImagesResponse {
  course_name: string;
  total_frames: number;
  generated: number;
  failed: number;
  images: BulkImageStatus[];
  message: string;
}

export interface GenerateVideoResponse {
  video_url: string;
  message: string;
}

export interface ImageState {
  frame_code: string;
  image_url: string;
  status: string;
}

export interface GetImagesResponse {
  course_name: string;
  images: ImageState[];
  count: number;
}

// ====================================================
// API Client
// ====================================================

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Upload file with course_name
   */
  async uploadFile(courseName: string, file: File): Promise<UploadFileResponse> {
    const formData = new FormData();
    formData.append('course_name', courseName);
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/files/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'File upload failed');
    }

    return response.json();
  }

  /**
   * Generate storyboard prompts
   */
  async generatePrompts(courseName: string): Promise<GeneratePromptResponse> {
    const response = await fetch(`${this.baseURL}/prompts/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ course_name: courseName }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Prompt generation failed');
    }

    return response.json();
  }

  /**
   * Get prompts by course_name
   */
  async getPrompts(courseName: string): Promise<{ course_name: string; prompt_json: StoryboardJSON; model_name: string }> {
    const response = await fetch(`${this.baseURL}/prompts/${courseName}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch prompts');
    }

    return response.json();
  }

  /**
   * Generate single image for a frame
   */
  async generateImage(courseName: string, frameCode: string): Promise<GenerateImageResponse> {
    const response = await fetch(`${this.baseURL}/images/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        course_name: courseName,
        frame_code: frameCode,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Image generation failed');
    }

    return response.json();
  }

  /**
   * Generate images for all frames (or specific video)
   */
  async generateBulkImages(
    courseName: string,
    videoNumber?: number
  ): Promise<GenerateBulkImagesResponse> {
    const response = await fetch(`${this.baseURL}/images/generate/bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        course_name: courseName,
        video_number: videoNumber,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Bulk image generation failed');
    }

    return response.json();
  }

  /**
   * Generate video (Production Flow)
   */
  async generateVideo(
    courseName: string,
    videoNumber: number,
    url1: string,
    url2?: string,
    motionPrompt?: string
  ): Promise<GenerateVideoResponse> {
    const response = await fetch(`${this.baseURL}/videos/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        course_name: courseName,
        video_number: videoNumber,
        url_1: url1,
        url_2: url2 || null,
        motion_prompt: motionPrompt || null
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Video generation failed');
    }

    return response.json();
  }

  /**
   * Get all generated images for a course
   */
  async getImages(courseName: string): Promise<GetImagesResponse> {
    const response = await fetch(`${this.baseURL}/images/${courseName}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch images');
    }

    return response.json();
  }

  /**
   * Get all videos for a course
   */
  async getVideos(courseName: string): Promise<any[]> {
    const response = await fetch(`${this.baseURL}/videos/${courseName}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch videos');
    }

    return response.json();
  }
}

export const apiClient = new APIClient();
