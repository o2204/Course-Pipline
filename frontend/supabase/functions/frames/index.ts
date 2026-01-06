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

    const url = new URL(req.url);
    const pathParts = url.pathname.split("/");
    const fileId = pathParts[pathParts.length - 1];

    if (!fileId) {
      return new Response(
        JSON.stringify({ error: "fileId is required" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    if (req.method === "GET") {
      // Fetch course with prompts and frame selections
      const { data: courseFile, error: courseError } = await supabase
        .from("course_files")
        .select("id, course_name, base_avatar_prompt, base_storyboard_prompt")
        .eq("id", fileId)
        .maybeSingle();

      if (courseError || !courseFile) {
        return new Response(
          JSON.stringify({ error: "Course not found" }),
          { status: 404, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }

      const { data: selections, error: selectionsError } = await supabase
        .from("video_frame_selections")
        .select("video_number, first_frame_url, middle_frame_url, third_frame_url, prompt_edit")
        .eq("course_file_id", fileId)
        .order("video_number");

      if (selectionsError) {
        console.error("Selections query error:", selectionsError);
      }

      return new Response(
        JSON.stringify({
          fileId: courseFile.id,
          courseName: courseFile.course_name,
          baseAvatarPrompt: courseFile.base_avatar_prompt,
          baseStoryboardPrompt: courseFile.base_storyboard_prompt,
          videos: selections || [],
        }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    if (req.method === "POST") {
      const { videos } = await req.json();

      if (!videos || !Array.isArray(videos)) {
        return new Response(
          JSON.stringify({ error: "videos array is required" }),
          { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }

      // Check if course exists
      const { data: courseFile, error: courseError } = await supabase
        .from("course_files")
        .select("id")
        .eq("id", fileId)
        .maybeSingle();

      if (courseError || !courseFile) {
        return new Response(
          JSON.stringify({ error: "Course not found" }),
          { status: 404, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }

      // Upsert frame selections
      const results = [];
      for (const video of videos) {
        const { data: existing } = await supabase
          .from("video_frame_selections")
          .select("id")
          .eq("course_file_id", fileId)
          .eq("video_number", video.videoNumber)
          .maybeSingle();

        if (existing) {
          const { data, error } = await supabase
            .from("video_frame_selections")
            .update({
              first_frame_url: video.firstFrameUrl,
              middle_frame_url: video.middleFrameUrl,
              third_frame_url: video.thirdFrameUrl,
              prompt_edit: video.promptEdit,
            })
            .eq("id", existing.id)
            .select()
            .single();

          if (!error) results.push(data);
        } else {
          const { data, error } = await supabase
            .from("video_frame_selections")
            .insert({
              course_file_id: fileId,
              video_number: video.videoNumber,
              first_frame_url: video.firstFrameUrl,
              middle_frame_url: video.middleFrameUrl,
              third_frame_url: video.thirdFrameUrl,
              prompt_edit: video.promptEdit,
            })
            .select()
            .single();

          if (!error) results.push(data);
        }
      }

      console.log(`Saved ${results.length} frame selections for course ${fileId}`);

      return new Response(
        JSON.stringify({ success: true, saved: results.length }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    return new Response(
      JSON.stringify({ error: "Method not allowed" }),
      { status: 405, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
