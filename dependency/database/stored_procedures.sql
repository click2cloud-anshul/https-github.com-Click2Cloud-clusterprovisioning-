CREATE OR REPLACE FUNCTION _cb_cp_sp_access_key_secret_key(p_users integer,
	cloud_type text) RETURNS SETOF json
    LANGUAGE plpgsql
    AS $BODY$
BEGIN
return query select array_to_json(array_agg(row_to_json(t))) as access_key_or_secret_key_details from (
SELECT 	_cb_credentials.client_id,	_cb_credentials.client_secret , _cb_credentials.tenant_id, _cb_credentials.subscription_id, ext_management_systems.name , ext_management_systems.id
FROM ext_management_systems
INNER JOIN _cb_credentials
ON ext_management_systems.name = _cb_credentials.name
Where
ext_management_systems.tenant_id IN (
	select MG.tenant_id
	from users U
	LEFT JOIN miq_groups_users MGU
	ON U.id = MGU.user_id
	LEFT JOIN miq_groups MG
	ON MGU.miq_group_id=MG.id
	WHERE U.id = p_users
)
AND ems_type=cloud_type

)as t;

END;
$BODY$;

ALTER FUNCTION _cb_cp_sp_access_key_secret_key_test(p_users integer,	cloud_type text)
    OWNER TO root;
