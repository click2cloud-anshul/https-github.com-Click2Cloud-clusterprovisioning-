CREATE TABLE IF NOT EXISTS _cb_cp_cluster_details(
	id serial NOT NULL PRIMARY KEY,
	user_id integer,
	provider_id integer,
	cluster_id text,
	cluster_details text,
	status text,
	created_at text,
	operation text
);

CREATE TABLE IF NOT EXISTS _cb_cp_cluster_config_details
(
    id serial NOT NULL,
    provider text,
    cluster_id text,
    cluster_public_endpoint text,
    cluster_config text,
    cluster_token text,
    PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS _cb_cp_s2i_details
(
    id serial primary key ,
    user_id bigint NOT NULL,
    created_at text NOT NULL,
    image character varying(100) NOT NULL,
    builder_image character varying(100) NOT NULL,
    github_url character varying(100)  NOT NULL,
    tag character varying(100)  NOT NULL,
    status character varying(50)  NOT NULL,
    comment text  NOT NULL,
    registry text NOT NULL
);

CREATE TABLE IF NOT EXISTS _cb_cr_namespace_details(
	id serial NOT NULL PRIMARY KEY,
	user_id integer,
	provider_id integer,
	namespace_id text,
	namespace_details text,
	status text,
	created_at text,
	operation text
);

CREATE TABLE IF NOT EXISTS _cb_cr_repository_details(
	id serial NOT NULL PRIMARY KEY,
	user_id integer,
	provider_id integer,
	repository_id text,
	repository_details text,
	status text,
	created_at text,
	operation text
);

CREATE TABLE IF NOT EXISTS public._cb_cp_instance_details
(
    id  serial NOT NULL PRIMARY KEY,
    cloud_provider text,
    zone_id text,
    instance_details text
);