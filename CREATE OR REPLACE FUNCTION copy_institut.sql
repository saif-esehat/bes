CREATE OR REPLACE FUNCTION copy_institute_id_from_schedule_ccmc()
RETURNS void AS $$
DECLARE
    my_variable INT;
    ins_code CHAR(10);
    schedule_row RECORD;
BEGIN
    FOR schedule_row IN (SELECT ccmc_candidate FROM ccmc_exam_schedule) LOOP
        -- Fetch institute_id based on gp_candidate
        SELECT institute_id INTO my_variable FROM ccmc_candidate WHERE ID = schedule_row.ccmc_candidate;
        
        -- Fetch institute_code based on institute_id
        SELECT code INTO ins_code FROM bes_institute WHERE ID = my_variable;

        -- Update gp_exam_schedule with the fetched institute_code
        UPDATE ccmc_exam_schedule
        SET institute_code = ins_code
        WHERE ccmc_candidate = schedule_row.ccmc_candidate;

        RAISE NOTICE 'Updated institute_code for ccmc_candidate %: %', schedule_row.gp_candidate, ins_code;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
