CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE tanuki_bot_mvc (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    embedding vector(1536) NOT NULL,
    url text NOT NULL,
    content text NOT NULL,
    metadata jsonb NOT NULL,
    chroma_id text,
    CONSTRAINT check_5df597f0fb CHECK ((char_length(url) <= 2048)),
    CONSTRAINT check_67053ce605 CHECK ((char_length(content) <= 8192)),
    CONSTRAINT check_e130e042d4 CHECK ((char_length(chroma_id) <= 512))
);

CREATE SEQUENCE tanuki_bot_mvc_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE tanuki_bot_mvc_id_seq OWNED BY tanuki_bot_mvc.id;

ALTER TABLE ONLY tanuki_bot_mvc ALTER COLUMN id SET DEFAULT nextval('tanuki_bot_mvc_id_seq'::regclass);

ALTER TABLE ONLY tanuki_bot_mvc
    ADD CONSTRAINT tanuki_bot_mvc_pkey PRIMARY KEY (id);

CREATE UNIQUE INDEX index_tanuki_bot_mvc_on_chroma_id ON tanuki_bot_mvc USING btree (chroma_id);
