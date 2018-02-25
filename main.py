from app import app, db
from app.models import User, Level, Activity


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Level': Level,
        'Activity': Activity,
    }


@app.cli.command()
def routes():
    from urllib.parse import unquote
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = unquote("{:20s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)
    for line in sorted(output):
        print(line)
