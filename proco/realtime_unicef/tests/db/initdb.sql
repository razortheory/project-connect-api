-- clean managed tables
drop sequence if exists public.measurements_id_seq;
drop table if exists public.measurements;

-- create tables & relations
CREATE TABLE public.measurements (
    id SERIAL PRIMARY KEY,
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
