(SELECT DISTINCT nom,ligne FROM noms_lignes WHERE nom = 'CHATELET LES HALLES');

 SELECT DISTINCT A.nom,A.ligne,B.nom,B.ligne,C.nom 
 FROM noms_lignes as A, noms_lignes as B,noms_lignes as C 
 WHERE C.nom = 'PIERREFITTE STAINS' and A.nom = 'CHATELET LES HALLES' AND A.ligne = B.ligne AND C.ligne = B.ligne ;

SELECT distinct A.nom, A.ligne, B.nom, C.ligne,  D.nom FROM noms_lignes as A, noms_lignes as B, noms_lignes as C, noms_lignes as D WHERE A.nom = 'CHATELET LES HALLES' AND D.nom = 'PIERREFITTE STAINS' AND A.ligne = B.ligne AND B.nom = C.nom AND C.ligne = D.ligne AND A.ligne <> C.ligne AND A.nom <> B.nom AND B.nom <> D.nom;

(ABS(lat - 48.82694828196076 ) + ABS( lng - 2.367038433387592)) 


WITH montab as (SELECT nom, CAST( latitude as FLOAT) as lat1 , CAST(longitude as FLOAT) as lng1,(ABS(CAST( latitude as FLOAT) - {lat} ) + ABS( CAST( latitude as FLOAT) - {lng})) as distance FROM network_node GROUP BY nom,lat1,lng1,distance) SELECT montab.nom FROM montab WHERE montab.distance = (SELECT min(montab.distance) FROM montab);

WITH montab as ( SELECT nom_long,latitude,longitude,(ABS(latitude - {lat} ) + ABS( longitude - {lng})) as distance 
				FROM metros GROUP BY nom_long,latitude,longitude,distance)
				
				SELECT montab.nom_long FROM montab WHERE montab.distance = (SELECT min(montab.distance) FROM montab);


															/*
WITH montab as ( SELECT nom,FLOAT(latitude) as lat ,FLOAT(longitude) as lng,(ABS(lat - 48.82694828196076 ) + ABS( lng - 2.367038433387592)) as distance 
				FROM network_node GROUP BY nom,latitude,longitude,distance)
SELECT montab.nom 
FROM montab 
WHERE montab.distance = (SELECT min(montab.distance) 
						 FROM montab)
															*/