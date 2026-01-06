# Course Visual Generation Platform - Technical Documentation

## 1. Project Overview
*   **Problem Solved**: Automates the creation of visual content (storyboards, images, and videos) from text-based course documents, reducing manual effort for content creators.
*   **High-Level Workflow**:
    1.  User uploads a course document (PDF/DOCX/TXT).
    2.  System parses text and generates a structured JSON storyboard.
    3.  AI generates visual prompts for each scene.
    4.  AI generates high-quality images for each frame.
    5.  AI animates images into short video clips.

## 2. System Architecture
*   **Frontend**: React (Vite), TypeScript, Tailwind CSS, Shadcn UI.
*   **Backend**: FastAPI (Python), Async SQLAlchemy.
*   **Database**: PostgreSQL (Supabase) for structured data (courses, prompts, mappings).
*   **AI Services**:
    *   **LLM**: OpenAI (GPT-4) for parsing and prompt generation.
    *   **Visuals**: Higgsfield AI for image and video generation.
*   **Storage**: Cloud Object Storage (Supabase) for assets.

## 3. Project Phases

### Phase 1: File Upload & Parsing
*   **Input**: Course file (`.docx`, `.pdf`, `.txt`) + Unique `course_name`.
*   **Output**: Extracted plain text stored in database.
*   **Responsibility**: Validate file format, ensure `course_name` uniqueness, and persist raw content.

### Phase 2: Validation & Structure
*   **Input**: Raw text or JSON structure.
*   **Output**: Validated JSON Storyboard.
*   **Responsibility**: Ensure content follows the strict hierarchy: **Videos -> Shots -> Frames**.

### Phase 3: Prompt Generation
*   **Input**: Course text.
*   **Output**: JSON Storyboard with detailed AI prompts (`scene_en`, `frame_prompt`).
*   **Responsibility**: Use LLM to break down text into visual scenes and write descriptive prompts for image generation.

### Phase 4: Image Generation
*   **Input**: `frame_prompt` from storyboard.
*   **Output**: High-resolution image URLs.
*   **Responsibility**: Generate visuals for every frame defined in the storyboard using text-to-image models.

### Phase 5: Video Generation
*   **Input**: Start Frame (Image URL) + End Frame (Optional) + Motion Prompt.
*   **Output**: Video URL (`.mp4`).
*   **Responsibility**: Animate static images into video clips (Image-to-Video).

## 4. Backend API Summary

| Endpoint | Method | Purpose | Main Input | Main Output |
| :--- | :--- | :--- | :--- | :--- |
| `/files/upload` | `POST` | Upload & parse course file | File, `course_name` | `file_id` |
| `/prompts/generate` | `POST` | Generate AI storyboard | `course_name` | JSON Storyboard |
| `/prompts/{course_name}` | `GET` | Retrieve existing storyboard | `course_name` | JSON Storyboard |
| `/images/generate` | `POST` | Generate single frame image | `course_name`, `frame_code` | Image URL |
| `/images/generate/bulk` | `POST` | Generate images for all frames | `course_name` | Status report |
| `/images/{course_name}` | `GET` | Get all course images | `course_name` | List of Image URLs |
| `/videos/generate` | `POST` | Generate video from image(s) | `url_1`, `url_2` (opt), `prompt` | Video URL |
| `/videos/{course_name}` | `GET` | Get all generated videos | `course_name` | List of Video URLs |

## 5. Frontend ↔ Backend Integration
*   **Communication**: Frontend uses HTTP requests (via `axios` or `fetch`) to communicate with the stateless Backend API.
*   **State Management**: `course_name` is the session key. The frontend "rehydrates" its state by fetching data (prompts, images) using the `course_name` when the user navigates or refreshes.
*   **Data Reactivity**: using `React Query` (TanStack Query) for catching, loading states, and automatic re-fetching.
*   **Error Handling**: Backend returns standard HTTP codes (`400`, `404`, `500`). Frontend intercepts these to show user-friendly toasts or error boundaries.

## 6. Data Flow Summary
1.  **User** uploads a document via Frontend.
2.  **Backend** parses text and creates a `File` record.
3.  **Frontend** triggers "Generate Structure".
4.  **Backend** (OpenAI) creates structured JSON and saves it.
5.  **User** reviews storyboard and clicks "Generate Images".
6.  **Backend** (Higgsfield) generates images and updates DB records.
7.  **Frontend** displays images; User selects frames for video.
8.  **Backend** generates video and returns URL.

## 7. Key Design Decisions
*   **`course_name` as Identifier**: Uses a human-readable, immutable slug as the primary key for routing and resource lookups across the system.
*   **JSON-Native Workflow**: The entire course structure (videos/shots/frames) is stored as a JSON blob, allowing flexibility without rigid relational schema changes.
*   **Separation of Concerns**: Strict layering: `Router` (HTTP) -> `Service` (Business Logic) -> `Repo` (DB Access).
*   **Idempotency**: Generation endpoints check if a resource already exists before re-generating to save costs and time.

## 8. System Evolution (Before vs After)

The project has undergone a major refactoring to transition from a robust prototype to a scalable, production-ready platform.

### Before Refactor
*   **Limited API**: Only 3 backend endpoints with unclear responsibilities.
*   **Restricted Input**: Upload endpoint accepted only `.doc` files.
*   **No Architecture**: Business logic mixed directly with routes; no separation of concerns.
*   **Backend Only**: No frontend application existed.
*   **Security Risks**: Scripts and internal assets committed directly to the repo; sensitive data exposed.
*   **Unclear Flow**: No clear data generation pipeline; hard to scale or maintain.

### After Refactor
*   **Scalable API**: Dedicated endpoints for every stage: upload, validation, prompt/image/video generation.
*   **Workflow Support**: Structured, course-based workflows.
*   **Clean Architecture**: Separation of concerns via **Routes → Services → Repositories → Database**.
*   **Integrated Frontend**: React frontend communicating via HTTP APIs.
*   **Security & Safety**: Removal of internal scripts/data; secure asset handling.
*   **Best Practices**: Clear separation of config and logic; production-ready structure.

**Summary**: This evolution has significantly enhanced **maintainability, security, and scalability**, ensuring seamless frontend-backend integration and providing a solid foundation for future growth.
