-- clean managed tables
drop sequence if exists public.measurements_id_seq;
drop table if exists public.measurements;

-- create tables & relations
CREATE TABLE public.measurements (
    id bigint NOT NULL,
    "timestamp" timestamp with time zone,
    uuid text,
    browser_id text,
    school_id text NOT NULL,
    device_type text,
    notes text,
    client_info jsonb,
    server_info jsonb,
    annotation text,
    download double precision,
    upload double precision,
    latency bigint,
    results jsonb
);
CREATE SEQUENCE public.measurements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE ONLY public.measurements
    ALTER COLUMN id
        SET DEFAULT nextval('public.measurements_id_seq'::regclass);
ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurements_pkey PRIMARY KEY (id);
