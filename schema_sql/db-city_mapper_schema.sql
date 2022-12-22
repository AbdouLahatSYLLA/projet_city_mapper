
/*CREATE DATABASE city_mapper;*/

/*
CREATE TABLE network_bus ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT,PRIMARY KEY (from_stop_I,to_stop_I,route_I_counts)  );

CREATE TABLE network_rail ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT,PRIMARY KEY (from_stop_I,to_stop_I,route_I_counts,n_vehicles)  );

CREATE TABLE network_subway ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT,PRIMARY KEY (from_stop_I,to_stop_I,route_I_counts)  );

CREATE TABLE network_tram ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT,PRIMARY KEY (from_stop_I,to_stop_I,route_I_counts) );

CREATE TABLE network_node ( stop_I NUMERIC(10,2),latitude TEXT ,longitude TEXT ,nom VARCHAR(100), PRIMARY KEY (stop_I,latitude,longitude) );
*/
CREATE TABLE network_walk (from_stop_I NUMERIC (10, 0),to_stop_I NUMERIC (10, 0),d NUMERIC (10, 0),d_walk NUMERIC (10, 0) );

CREATE TABLE routes(liste_arrets TEXT,route_type NUMERIC(1),route_I NUMERIC(4),route_name VARCHAR(32) );

CREATE TABLE lignes(nom VARCHAR(32),stations TEXT,route_type NUMERIC(1));

CREATE TABLE network_combined ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT,route_type NUMERIC(2,0) ,PRIMARY KEY (from_stop_I,to_stop_I,route_type) );

CREATE TABLE noms_lignes(nom TEXT,ligne TEXT,route_type NUMERIC(1));

CREATE TABLE network_node ( stop_I NUMERIC(10,2),latitude TEXT ,longitude TEXT ,nom VARCHAR(100), PRIMARY KEY (stop_I,latitude,longitude) );
