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
    const videoNumber = url.searchParams.get("videoNumber");

    if (!fileId) {
      return new Response(
        JSON.stringify({ error: "fileId is required" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Check if course exists
    const { data: courseFile, error: courseError } = await supabase
      .from("course_files")
      .select("id, course_name")
      .eq("id", fileId)
      .maybeSingle();

    if (courseError || !courseFile) {
      return new Response(
        JSON.stringify({ error: "Course not found" }),
        { status: 404, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Build query for images
    let query = supabase
      .from("video_images")
      .select("video_number, image_index, image_url")
      .eq("course_file_id", fileId)
      .order("video_number")
      .order("image_index");

    if (videoNumber) {
      query = query.eq("video_number", parseInt(videoNumber));
    }

    const { data: images, error: imagesError } = await query;

    if (imagesError) {
      console.error("Images query error:", imagesError);
      return new Response(
        JSON.stringify({ error: "Failed to fetch images" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    if (videoNumber) {
      return new Response(
        JSON.stringify({
          fileId: courseFile.id,
          courseName: courseFile.course_name,
          videoNumber: parseInt(videoNumber),
          images: images?.map((img) => ({
            imageUrl: img.image_url,
            imageIndex: img.image_index,
          })) || [],
        }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    return new Response(
      JSON.stringify({
        fileId: courseFile.id,
        courseName: courseFile.course_name,
        images: images || [],
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
