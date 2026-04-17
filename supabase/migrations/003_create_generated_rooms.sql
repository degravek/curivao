CREATE TABLE generated_rooms (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    design_intent text NOT NULL,
    dominant_style text,
    color_palette text[],
    selected_pieces jsonb NOT NULL,
    image_gen_prompt text,
    image_url text,
    published boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now()
);
