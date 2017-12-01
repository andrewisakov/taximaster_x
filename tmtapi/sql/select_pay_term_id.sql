select id, opertime, driverid from driver_oper where term_id=? and coalesce(deleted, 0)=0
