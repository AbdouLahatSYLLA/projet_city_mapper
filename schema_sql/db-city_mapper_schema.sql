
/*CREATE DATABASE city_mapper;*/


CREATE TABLE network_walk (from_stop_I NUMERIC (10, 0),to_stop_I NUMERIC (10, 0),d NUMERIC (10, 0),d_walk NUMERIC (10, 0) );

CREATE TABLE routes(liste_arrets TEXT,route_type NUMERIC(1),route_I NUMERIC(4),route_name VARCHAR(32) );

CREATE TABLE lignes(nom VARCHAR(32),stations TEXT,route_type NUMERIC(1));

CREATE TABLE noms_lignes(nom TEXT,ligne TEXT,route_type NUMERIC(1));

CREATE TABLE network_node ( stop_I NUMERIC(5),latitude TEXT ,longitude TEXT ,nom TEXT, PRIMARY KEY (stop_I) );
