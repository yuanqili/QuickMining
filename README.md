# Modern Flask

Yuanqi Ricky Li (C) Feb 2018, UC Santa Barbara

## Usage

### Virtual environment

```
$ virtualenv venv # creates a new virenv under folder ./venv
$ source venv/bin/activate # activates the virenv just created
(venv) $ deactivate # deactivates the virenv
```

### Flask

```
(venv) $ export FLASK_APP=main.py # sets up the Flask application entry
(venv) $ flask shell # Flask's shell context
```

### Migration

```
(venv) $ flask db init
(venv) $ flask db migrate -m "message"
(venv) $ flask db upgrade/downgrade
```

After you modify the models in your application you generate a new migration
script using `flask db migrate`, you probably review it to make sure the
automatic generation did the right thing, and then apply the changes to your
*development database* using `flask db upgrade`. You will add the migration
script to source control and commit it.

When you are ready to release the new version of the application to your
*production server*, all you need to do is grab the updated version of your
application, which will include the new migration script, and run
`flask db upgrade`. Alembic will detect that the production database is not
updated to the latest revision of the schema, and run all the new migration
scripts that were created after the previous release.

You also have a `flask db downgrade` command, which undoes the last migration.
While you will be unlikely to need this option on a *production system*, you may
find it very useful during *development*.

### SMTP Server

```
(venv) $ python3 -m smtpd -n -c DebuggingServer localhost:8025
(venv) $ export MAIL_SERVER=localhost
(venv) $ export MAIL_PORT=8025
```

The command above creates a SMTP debugging server from Python, which accepts
emails, but instead of sending them, it prints them to the console.

Note that port `8025` may require privilege.

To setup the mail service, set the following environs:

```
(venv) $ export MAIL_SERVER=smtp.googlemail.com
(venv) $ export MAIL_PORT=587
(venv) $ export MAIL_USE_TLS=1
(venv) $ export MAIL_USERNAME=<your-gmail-username>
(venv) $ export MAIL_PASSWORD=<your-gmail-password>
```

The security features in your Gmail account may prevent the application from sending emails through it unless you
explicitly allow "less secure apps" access to your Gmail account.
