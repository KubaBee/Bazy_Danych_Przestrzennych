--4
SELECT COUNT(popp.f_codedesc) FROM popp, majrivers WHERE st_length(st_shortestline(popp.geom, majrivers.geom)) < 1000 and popp.f_codedesc = 'Building'
SELECT popp.* INTO tableB FROM popp, majrivers WHERE st_length(st_shortestline(popp.geom, majrivers.geom)) < 1000 and popp.f_codedesc = 'Building'
--5
SELECT name, geom, elev INTO airportsNew FROM airports;
--a.1
SELECT name FROM airportsNew ORDER BY st_x(geom) LIMIT 1;
--a.2
SELECT name FROM airportsNew ORDER BY st_x(geom) DESC LIMIT 1;
--b ST_Line_Interpolate_Point
INSERT INTO airportsNew VALUES ('airportB', (SELECT st_centroid (st_makeLine(
    (SELECT geom FROM airportsNew WHERE name = 'ATKA'),
    (SELECT geom FROM airportsNew WHERE name = 'ANNETTE ISLAND')))),123);
--6
SELECT st_area(st_buffer(st_shortestline(l.geom, ap.geom),1000)) FROM lakes l, airports ap
WHERE l.names = 'Iliamna Lake' and ap.name = 'AMBLER';
--7
SELECT SUM(st_area(tr.geom)), tr.vegdesc FROM trees tr, swamp s, tundra tun
WHERE st_contains(tr.geom, s.geom) OR st_contains(tr.geom, tun.geom) GROUP BY tr.vegdesc;