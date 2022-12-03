
/*CREATE DATABASE paris_mapper;*/



CREATE TABLE network_bus ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT, PRIMARY KEY (from_stop_I,to_stop_I) );

CREATE TABLE network_rail ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT,PRIMARY KEY (from_stop_I,to_stop_I) );

CREATE TABLE network_subway ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT,PRIMARY KEY (from_stop_I,to_stop_I) );

CREATE TABLE network_tram ( from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),duration_avg NUMERIC(10,2),n_vehicles NUMERIC(10,2), route_I_counts TEXT,PRIMARY KEY (from_stop_I,to_stop_I) );

CREATE TABLE stops ( stop_I NUMERIC(10,2),latitude NUMERIC(10,2) ,longitude NUMERIC(10,2) ,nom VARCHAR(100), PRIMARY KEY (stop_I) );

CREATE TABLE network_walk (from_stop_I NUMERIC(10,2),to_stop_I NUMERIC(10,2),d NUMERIC(10,2),d_walk NUMERIC(10,2) );

CREATE TABLE ROUTES (coordinates text , route_type NUMERIC(2,0),route_I NUMERIC(10,2), route_name NUMERIC(10,2));

CREATE TABLE moyen_transport(mode VARCHAR(32), id NUMERIC(5,0), PRIMARY KEY(id) );
