
CREATE DATABASE app_city_mapper;

/* AUTEUR:  ABDOU LAHAT SYLLA 12011836, MURSAL ZUHAIR 12008351 */

CREATE TABLE network_walk (from_stop_I NUMERIC (10, 0),to_stop_I NUMERIC (10, 0),d NUMERIC (10, 0),d_walk NUMERIC (10, 0),PRIMARY KEY (from_stop_I,to_stop_I));

CREATE TABLE network_node ( stop_I NUMERIC(5),latitude TEXT ,longitude TEXT ,nom TEXT, PRIMARY KEY (stop_I) );

CREATE TABLE noms_lignes(nom TEXT,ligne TEXT,route_type NUMERIC(1),PRIMARY KEY(nom,ligne,route_type));

CREATE TABLE routes(liste_arrets TEXT,route_type NUMERIC(1),route_I NUMERIC(4),route_name TEXT, PRIMARY KEY(route_i));
