from flask import Flask, render_template, request, json, session
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin

from files.security import *
from files.config import *
import os


app = Flask(__name__)
CORS(app, supports_credentials=True, origin='http://localhost:3000')


app.config['SECRET_KEY'] = 'testing testing 123'  # os.urandom(24)
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB

mysql = MySQL(app)


@app.route('/signup', methods=['POST'])
def signup():
    email = request.json['email']
    username = request.json['username']
    password = encrypt_password(request.json['password'])

    # if username is None or password is None:
    #     abort(400)  # missing arguments

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM users WHERE user_email = %s",
                [email])
    if cur.rowcount != 0:
        cur.close()
        return 'EMAIL_EXISTS'

    cur.execute("SELECT * FROM users WHERE user_username = %s",
                [username])
    if cur.rowcount != 0:
        cur.close()
        return 'USERNAME_EXISTS'

    cur.execute("INSERT INTO users(user_email, user_username, user_password) VALUES ( %s, %s, %s)", [
                email, username, password])
    mysql.connection.commit()
    cur.close()
    return 'SUCCESS'


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT user_id, user_password FROM users WHERE user_username = %s", [username])

    if cur.rowcount == 0:
        cur.close()
        return 'USER_NOT_FOUND'

    rv = cur.fetchall()

    print(rv[0][0])

    if check_encrypted_password(password, rv[0][1]):
        session['user_id'] = rv[0][0]
        session['password'] = password
        cur.close()
        return ('AUTH_SUCCESS')

    return 'AUTH_FAILED'


@app.route('/get-account-info', methods=['GET'])
def get_account_info():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_username, user_permission, user_email FROM users WHERE user_id = %s", [
            session['user_id']])

        if cur.rowcount == 0:
            cur.close()
            return 'USER_NOT_FOUND'

        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return json.dumps(json_data)


@app.route('/update-account', methods=['POST'])
def update_account():
    if session['password'] != request.form.get('password'):
        return 'AUTH_FAILED'

    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        cur = mysql.connection.cursor()

        if 'username' in request.form:
            cur.execute('SELECT * FROM users WHERE user_username = %s', [
                        request.form.get('username')])
            if cur.rowcount != 0:
                cur.close()
                return 'USERNAME_TAKEN'
            
        if 'email' in request.form:
            cur.execute('SELECT * FROM users WHERE user_email = %s', [
                        request.form.get('email')])
            if cur.rowcount != 0:
                cur.close()
                return 'EMAIL_IN_USE'

                
        if 'username' in request.form:
            cur.execute('UPDATE users SET user_username = %s WHERE user_id = %s', [
                        request.form.get('username'), session['user_id']])
            mysql.connection.commit()

        if 'email' in request.form:
            cur.execute('UPDATE users SET user_email = %s WHERE user_id = %s', [
                        request.form.get('email'), session['user_id']])
            mysql.connection.commit()

        if 'newpass' in request.form:
            password = encrypt_password(request.form.get('password'))
            cur.execute('UPDATE users SET user_password = %s WHERE user_id = %s', [
                        password, session['user_id']])
            mysql.connection.commit()
        return 'ACCOUNT_UPDATED'

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('password', None)

    return "LOGGED_OUT"


@app.route('/session', methods=['GET'])
def checksession():
    if 'user_id' and 'password' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_password FROM users WHERE user_id = %s", [
                    session['user_id']])

        if cur.rowcount == 0:
            cur.close()
            return 'USER_NOT_FOUND'

        rv = cur.fetchall()

        if check_encrypted_password(session['password'], rv[0][0]):
            cur.close()
            return ('AUTH_SUCCESS')
    return 'AUTH_FAILED'


@app.route('/get-my-campaigns', methods=['GET'])
def getmycampaigns():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT campaign_id, campaign_name FROM campaigns WHERE campaign_owner_id = %s", [
                    session['user_id']])
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return json.dumps(json_data)


@app.route('/get-my-characters', methods=['GET'])
def getmycharacters():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT character_id, character_name FROM characters WHERE character_owner_id = %s", [
                    session['user_id']])
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return json.dumps(json_data)


@app.route('/get-campaign', methods=['GET'])
def getcampaign():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        campaign_id = request.args.get('campaign_id')
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM campaigns WHERE campaign_id = %s", [campaign_id])
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))

        cur.execute(
            "SELECT character_name, character_background, character_owner_id, character_id FROM characters c JOIN campaigns camp ON c.character_campaign_id = camp.campaign_id WHERE camp.campaign_id = %s", [campaign_id])
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))

        return json.dumps(json_data)


@app.route('/get-character', methods=['GET'])
def get_character():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        character_id = request.args.get('character_id')
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM characters WHERE character_id = %s", [character_id])
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))

        return json.dumps(json_data)


@app.route('/create-character', methods=['POST'])
def create_character():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        character_name = request.form.get('character_name')
        character_background = request.form.get('character_background')
        owner_id = session['user_id']

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO characters (character_owner_id, character_name, character_background) VALUES (%s, %s, %s)", [
                    owner_id, character_name, character_background])
        mysql.connection.commit()
        cur.close()

        return 'CHARACTER_CREATED'


@app.route('/edit-character', methods=['POST'])
def edit_character():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        character_name = request.form.get('character_name')
        character_background = request.form.get('character_background')
        character_id = request.form.get('character_id')
        owner_id = session['user_id']

        cur = mysql.connection.cursor()

        cur.execute("SELECT character_owner_id FROM characters WHERE character_id = %s", [
                    character_id])
        rv = cur.fetchall()
        character_owner_id = rv[0][0]

        if(character_owner_id != owner_id):
            return 'OWNER_AUTH_FAILED'

        cur.execute("UPDATE characters SET character_name = %s, character_background = %s WHERE character_id = %s", [
                    character_name, character_background, character_id])
        mysql.connection.commit()
        cur.close()

        return 'CHARACTER_UPDATED'


@app.route('/delete-character', methods=['DELETE'])
def delete_character():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        character_id = request.args.get('character_id')
        owner_id = session['user_id']

        cur = mysql.connection.cursor()

        cur.execute("SELECT character_owner_id FROM characters WHERE character_id = %s", [
                    character_id])
        rv = cur.fetchall()
        character_owner_id = rv[0][0]

        if(character_owner_id != owner_id):
            return 'OWNER_AUTH_FAILED'

        cur.execute(
            "DELETE FROM characters WHERE character_id = %s", [character_id])
        mysql.connection.commit()
        cur.close()

        return 'CHARACTER_DELETED'


@app.route('/create-campaign', methods=['POST'])
def create_campaign():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        campaign_name = request.form.get('campaign_name')
        campaign_desc = request.form.get('campaign_desc')
        owner_id = session['user_id']

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO campaigns (campaign_owner_id, campaign_name, campaign_desc) VALUES (%s, %s, %s)", [
                    owner_id, campaign_name, campaign_desc])
        mysql.connection.commit()
        cur.close()

        return 'CAMPAIGN_CREATED'


@app.route('/edit-campaign', methods=['POST'])
def edit_campaign():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        campaign_name = request.form.get('campaign_name')
        campaign_desc = request.form.get('campaign_desc')
        campaign_id = request.form.get('campaign_id')
        owner_id = session['user_id']

        cur = mysql.connection.cursor()

        cur.execute("SELECT campaign_owner_id FROM campaigns WHERE campaign_id = %s", [
                    campaign_id])
        rv = cur.fetchall()
        campaign_owner_id = rv[0][0]

        if(campaign_owner_id != owner_id):
            return 'OWNER_AUTH_FAILED'

        cur.execute("UPDATE campaigns SET campaign_name = %s, campaign_desc = %s WHERE campaign_id = %s", [
                    campaign_name, campaign_desc, campaign_id])
        mysql.connection.commit()
        cur.close()

        return 'CAMPAIGN_UPDATED'


@app.route('/delete-campaign', methods=['DELETE'])
def delete_campaign():
    if (checksession() != "AUTH_SUCCESS"):
        return checksession()
    else:
        campaign_id = request.args.get('campaign_id')
        owner_id = session['user_id']

        cur = mysql.connection.cursor()

        cur.execute("SELECT campaign_owner_id FROM campaigns WHERE campaign_id = %s", [
                    campaign_id])
        rv = cur.fetchall()
        campaign_owner_id = rv[0][0]

        if(campaign_owner_id != owner_id):
            return 'OWNER_AUTH_FAILED'

        cur.execute(
            "DELETE FROM campaigns WHERE campaign_id = %s", [campaign_id])
        mysql.connection.commit()
        cur.close()

        return 'CAMPAIGN_DELETED'


if __name__ == '__main__':
    app.run(debug=True)

# rv = cur.fetchall()
# row_headers=[x[0] for x in cur.description] #extracts row headers
# json_data=[]
# for result in rv:
#   json_data.append(dict(zip(row_headers,result)))
# return json.dumps(json_data)
