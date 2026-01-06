import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const formData = await req.formData();
    const courseNameInput = formData.get("courseName") as string;
    const file = formData.get("file") as File;

    if (!file) {
      return new Response(
        JSON.stringify({ error: "file is required" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Use provided name or derive from file name
    const courseName = courseNameInput?.trim() || file.name.replace(/\.[^/.]+$/, "") || "Untitled Course";

    // Upload file to storage
    const fileExt = file.name.split(".").pop();
    const fileName = `${crypto.randomUUID()}.${fileExt}`;
    const filePath = `courses/${fileName}`;

    const { error: uploadError } = await supabase.storage
      .from("course-files")
      .upload(filePath, file, {
        contentType: file.type,
        upsert: false,
      });

    if (uploadError) {
      console.error("Upload error:", uploadError);
      return new Response(
        JSON.stringify({ error: "Failed to upload file" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Generate base prompts
    const baseAvatarPrompt = `AI avatar for an eLearning course called '${courseName}'. Professional educator tone, friendly but clear, neutral background suitable for corporate learners. The avatar should appear knowledgeable and approachable, with natural gestures and expressions.`;
    
    const baseStoryboardPrompt = `Storyboard frames for eLearning video '${courseName}'. Clean corporate style, readable visuals, focus on key instructional moments for the avatar video. Use professional color palette, clear typography, and engaging compositions that support learning objectives.`;

    // Create course file record
    const { data: courseFile, error: dbError } = await supabase
      .from("course_files")
      .insert({
        course_name: courseName,
        file_path: filePath,
        base_avatar_prompt: baseAvatarPrompt,
        base_storyboard_prompt: baseStoryboardPrompt,
      })
      .select()
      .single();

    if (dbError) {
      console.error("Database error:", dbError);
      return new Response(
        JSON.stringify({ error: "Failed to create course record" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Generate some mock storyboard images for demo
    const mockImages = [];
    for (let video = 1; video <= 3; video++) {
      for (let frame = 1; frame <= 5; frame++) {
        mockImages.push({
          course_file_id: courseFile.id,
          video_number: video,
          image_index: frame,
          image_url: `https://picsum.photos/seed/${courseFile.id}-v${video}-f${frame}/800/450`,
        });
      }
    }

    const { error: imagesError } = await supabase
      .from("video_images")
      .insert(mockImages);

    if (imagesError) {
      console.error("Images insert error:", imagesError);
    }

    console.log(`Course created: ${courseFile.id} - ${courseName}`);

    return new Response(
      JSON.stringify({
        fileId: courseFile.id,
        courseName: courseFile.course_name,
        baseAvatarPrompt: courseFile.base_avatar_prompt,
        baseStoryboardPrompt: courseFile.base_storyboard_prompt,
        filePath: courseFile.file_path,
      }),
      { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
