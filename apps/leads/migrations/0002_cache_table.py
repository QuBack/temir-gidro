from django.core.management import call_command
from django.db import migrations


def create_cache_table(apps, schema_editor):
    # The lead rate limit lives in the database cache. Creating its table here
    # means a plain `migrate` is enough; the command is idempotent.
    call_command("createcachetable", database=schema_editor.connection.alias, verbosity=0)


class Migration(migrations.Migration):
    dependencies = [("leads", "0001_initial")]

    operations = [migrations.RunPython(create_cache_table, migrations.RunPython.noop)]
