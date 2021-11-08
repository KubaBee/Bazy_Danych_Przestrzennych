CREATE EXTENSION postgis;

--1
SELECT SUM(area_km2) FROM trees WHERE vegdesc = 'Mixed Trees';

--3
SELECT SUM(ST_Length(railroads.geom)) FROM railroads regions r
	WHERE ST_Within(railroads.geom, r.geom) and r.name_2 ='Matanuska-Susitna';
	
--4.a
SELECT AVG(elev) FROM airports WHERE use='Military';

--4.b
SELECT COUNT(gid) FROM airports WHERE use='Military';

--4.c
SELECT * FROM airports WHERE use='Military' AND elev > 1400;
--DELETE FROM airports WHERE use='Military' AND elev > 1400;

--5
SELECT popp.* FROM popp, regions r
WHERE ST_Within(popp.geom, r.geom) and r.name_2 ='Bristol Bay';
--DELETE popp FROM popp, rivers WHERE ST_Contains(popp.geom, ST_Buffer(rivers.geom, 100000))

--6 
SELECT ST_AsText(ST_Intersection(majrivers.geom, railroads.geom)) FROM majrivers, railroads

--7??

--8

SELECT ST_Union
	(ST_Difference(ST_Buffer(airports.geom,100000), ST_Buffer(railroads.geom,50000)),regions.geom)
FROM airports, railroads, regions;
