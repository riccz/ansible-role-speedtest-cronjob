Speedtest Cronjob
=================

This role sets up a systemd timer that periodically runs an
[Ookla speedtest](https://www.speedtest.net/apps/cli) and saves the results into a PostgreSQL DB.


DB Schema
---------

The result data is flattened and saved into a single table. The following SQL creates the schema.

```sql
CREATE TABLE results (
    timestamp TIMESTAMPTZ NOT NULL,
    ping_jitter DOUBLE PRECISION NOT NULL,
    ping_latency DOUBLE PRECISION NOT NULL,
    download_bandwidth DOUBLE PRECISION NOT NULL,
    download_bytes DOUBLE PRECISION NOT NULL,
    download_elapsed DOUBLE PRECISION NOT NULL,
    upload_bandwidth DOUBLE PRECISION NOT NULL,
    upload_bytes DOUBLE PRECISION NOT NULL,
    upload_elapsed DOUBLE PRECISION NOT NULL,
    packetLoss DOUBLE PRECISION NOT NULL,
    isp TEXT NOT NULL,
    interface_internalIp INET NOT NULL,
    interface_name TEXT NOT NULL,
    interface_macAddr MACADDR NOT NULL,
    interface_isVpn BOOLEAN NOT NULL,
    interface_externalIp INET NOT NULL,
    server_id BIGINT NOT NULL,
    server_name TEXT NOT NULL,
    server_location TEXT NOT NULL,
    server_country TEXT NOT NULL,
    server_host TEXT NOT NULL,
    server_port INTEGER NOT NULL,
    server_ip INET NOT NULL,
    result_id UUID PRIMARY KEY NOT NULL,
    result_url TEXT NOT NULL
);
CREATE INDEX results_timestamp_key ON results(timestamp DESC);
```

Requirements
------------

- Docker must be installed, as this role uses [this image from tianon](https://hub.docker.com/r/tianon/speedtest).
- PostgreSQL, with the DB schema already in place.
- The `ansible.utils` collection. Install with `ansible-galaxy collection install ansible.utils`.

Role Variables
--------------

- `speedtest_dburi`: DB URI where the results are saved.
- `speedtest_freq` (default `hourly`): Timer trigger frequency. This is a [systemd calendar value][systemd-time-calendar], so it can also take cronjob-like entries, e.g. `*-*-07 12:15:00`.
- `speedtest_random_delay`  (default 0): If nonzero, randomly delay the trigger between 0 and this many seconds.
- `speedtest_fixed_random_delay` (default false): Use a fixed random delay (if enabled). The timer will always trigger with the same delay (dependent on the machine-id). This can only be used on systemd versions >= 247.

[systemd-time-calendar]: https://www.freedesktop.org/software/systemd/man/systemd.time.html#Calendar%20Events

Example Playbook
----------------

```yaml
---
- hosts: host.example.com
  roles:
    - role: speedtest-cronjob
      vars:
        speedtest_dburi: "postgresql://user:pass@localhost:5432/dbname"
        # Every three hours, starting from 00:00:00, Italian timezone
        speedtest_freq: "*-*-* 00/3:00:00 Europe/Rome"
        # Run randomly between 0 and 15 minutes past the hour
        speedtest_random_delay: 900
...
```

License
-------

3-Clause BSD
