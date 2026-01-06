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
    
    const { videoNumber, imageIndex } = await req.json();

    if (!fileId || !videoNumber || !imageIndex) {
      return new Response(
        JSON.stringify({ error: "fileId, videoNumber, and imageIndex are required" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Generate a new mock image URL (in production, this would call an AI image generation API)
    const timestamp = Date.now();
    const newImageUrl = `https://picsum.photos/seed/${fileId}-v${videoNumber}-f${imageIndex}-${timestamp}/800/450`;

    // Update the image record
    const { data, error } = await supabase
      .from("video_images")
      .update({ image_url: newImageUrl })
      .eq("course_file_id", fileId)
      .eq("video_number", videoNumber)
      .eq("image_index", imageIndex)
      .select()
      .single();

    if (error) {
      console.error("Update error:", error);
      return new Response(
        JSON.stringify({ error: "Failed to regenerate image" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    console.log(`Regenerated image for course ${fileId}, video ${videoNumber}, frame ${imageIndex}`);

    return new Response(
      JSON.stringify({
        videoNumber,
        imageIndex,
        imageUrl: newImageUrl,
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
