CREATE OR REPLACE FUNCTION update_user_password() 
    RETURNS VOID 
AS $$
DECLARE
    candidate_row record;
    user_data res_users%ROWTYPE;
    new_password TEXT;
BEGIN
    FOR candidate_row IN (SELECT user_id FROM gp_candidate WHERE indos_no IN ('23GM6723','23GM6129') ) LOOP
        -- Search res_users table for the corresponding user_id
        BEGIN
            SELECT * INTO user_data FROM res_users WHERE id = candidate_row.user_id;

            -- If a matching record is found, update the password
            IF FOUND THEN
                -- Generate a new hashed password with a manually specified salt
                -- new_password := crypt(user_data.login || '1', '$2a$12$' || md5(random()::text));
                new_password :=  '12345678';

                -- Update the password in the res_users table
                -- UPDATE res_users SET password = new_password WHERE id = user_data.id;
                UPDATE res_users SET password = new_password WHERE login = user_data.id;

                RAISE NOTICE 'Password updated for User ID: %', user_data.login;
            ELSE
                RAISE NOTICE 'No matching record found for User ID: %', candidate_row.user_id;
            END IF;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                RAISE NOTICE 'No matching record found for User ID: %', candidate_row.user_id;
        END;

    END LOOP;

    -- End the function
    RETURN;
END;
$$ LANGUAGE plpgsql;
