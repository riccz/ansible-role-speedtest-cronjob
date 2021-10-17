#!/usr/bin/env python3

import json
import sys
import logging
import os

import psycopg2
from psycopg2 import sql

LOGGER = logging.getLogger("speedtest2pg")
PG_COLS = [
    "timestamp",
    "ping_jitter",
    "ping_latency",
    "download_bandwidth",
    "download_bytes",
    "download_elapsed",
    "upload_bandwidth",
    "upload_bytes",
    "upload_elapsed",
    "packetLoss",
    "isp",
    "interface_internalIp",
    "interface_name",
    "interface_macAddr",
    "interface_isVpn",
    "interface_externalIp",
    "server_id",
    "server_name",
    "server_location",
    "server_country",
    "server_host",
    "server_port",
    "server_ip",
    "result_id",
    "result_url",
]


def make_insert_sql():
    col_idents = sql.SQL(", ").join(sql.Identifier(c.lower()) for c in PG_COLS)
    val_phs = sql.SQL(", ").join(sql.Placeholder(c) for c in PG_COLS)
    return sql.SQL("INSERT INTO results ({}) VALUES ({})").format(col_idents, val_phs)


def flatten_dict(x):
    out = {}
    for k, v in x.items():
        if not isinstance(v, dict):
            out[k] = v
        else:
            for sk, sv in v.items():
                out_k = f"{k}_{sk}"
                assert out_k not in out
                out[out_k] = sv
    return out


result = json.load(sys.stdin)
assert result["type"] == "result"
del result["type"]
flat_result = flatten_dict(result)
assert set(flat_result.keys()) == set(PG_COLS)

DBURI = os.environ["SPEEDTEST2PG_DBURI"]
conn = psycopg2.connect(DBURI)
with conn:
    with conn.cursor() as curs:
        q = make_insert_sql()
        curs.execute(q, flat_result)
conn.close()

