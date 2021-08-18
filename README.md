# bluesky-autonomic

A project to add "reflexes" to bluesky settable devices.

## happi

Create config file at `~/.config/happi/happi.ini`

```
[DEFAULT]
path = ~/.local/share/happi/db.json
```

Populate environment variable.

```bash
$ export HAPPI_CFG=~/.config/happi/happi.ini
```

Dump all yaq devices into database.
Note that if you do this again all devices with the same name will be rewritten.

```bash
$ yaqd list -f happi | happi update
```

Manually edit `device_class` field, putting in `wright.DelayDevice` and `wright.OPADevice` where appropriate. Also edit type field.

Test it out in Python.

```python
import appdirs
import pathlib
import happi

# make happi client
db_path = pathlib.Path(appdirs.user_data_dir("happi")) / "db.json"
happi_backend = happi.backends.backend(db_path)
happi_client = happi.Client(database=happi_backend)

# search
happi_client.load_device(name="d1")
```