SELECT first_name, last_name 
                INTO BEST_CUSTOMERS_401476
                FROM customers_401476 WHERE ST_DistanceSpheroid( 
                ST_SetSRID(location::geometry,0), ST_Point(-75.67329768604034,41.39988501005976),
                'SPHEROID["WGS 84",6378137,298.257223563]')/1000 < 50