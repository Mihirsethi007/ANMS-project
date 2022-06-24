import globals
from re import L
import json
import time
from unicodedata import name
# from flask import Flask, render_template
# import pymysql
from flask import Blueprint, Flask, jsonify, redirect,render_template, request,flash, send_file , url_for,session,render_template_string
# from sqlalchemy.sql import text
from flask_mysqldb import MySQL
import firebase_admin
from firebase_admin import auth, credentials
import os
from importlib_metadata import method_cache
from werkzeug.utils import secure_filename
from datetime import timedelta

cred = credentials.Certificate(os.getcwd()+"/serviceAccountKey.json")
firebase_admin.initialize_app(cred)


# app = Flask(__name__)

# # change to name of your database; add path if necessary
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'pb.py'
# app.config['MYSQL_DB'] = 'user_test'

app = Flask(__name__,template_folder='templates', static_folder='static')


app.config['SECRET_KEY']="sshhh"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mihirbhai'
app.config['UPLOAD_PATH'] = 'upload'
app.config['UPLOAD_EXTENSIONS'] = ['.pdf',',jpeg']
app.config['MAX_CONTENT_LENGTH'] = 2048 * 2048

# this variable, db, will be used for all SQLAlchemy commands
mysql = MySQL(app)



@app.route("/")
def welcome():
    return render_template('main_scr.html')


@app.route('/admin', methods = ['POST', 'GET'])
def admin_render():
        # fields = request.args.get("ph")
        if "verno" in session and session['verno'] == '19876543210':
            cursor = mysql.connection.cursor()
            cursor.execute("select CONCAT_WS( ', ', ty_gn_hy1,ty_gn_hy2,ty_gn_hy3,ty_gn_hywal,ty_gn_hy4,ty_gn_hy5,ty_gn_hy6,ty_of_hy7 ), phn,name,address, contact_no, language, CONCAT_WS( ', ', ty_gn,ty_dr,ty_fl,ty_wal,ty_wel,ty_cnc,ty_wh,ty_of ),pref_loc from users") 
            data = cursor.fetchall() #data from database 
            # print(data)
            mysql.connection.commit()
            cursor.close()
            return render_template("admin_portal.html", value=data)
        return redirect(url_for('auth_render'))

@app.route('/managerList', methods = ['POST', 'GET'])
def managerList_render():
        # fields = request.args.get("ph")
        if 'verno' in session and session['verno'] == '19876543210':
            cursor = mysql.connection.cursor()
            cursor.execute("select * from managers") 

            data = cursor.fetchall() #data from database 
            print(data)
            mysql.connection.commit()
            cursor.close()
            return render_template("managerList.html", value=data)
        return redirect(url_for('auth_render'))

@app.route('/deletemanager', methods=['POST'])
def delete_manager():
    if 'verno' in session and session['verno'] == '19876543210':
        try:
            if request.method == 'POST':
                qtc_data = request.get_json()
                ph_no = qtc_data["phno"]
                print(ph_no)
                cursor = mysql.connection.cursor()
                cursor.execute(" DELETE FROM managers WHERE phone ="+ph_no)
                mysql.connection.commit()
                cursor.close()
                return jsonify({'status':200,'message':'success'})
        except Exception as e:
            print(e)
            return jsonify({'status':404,'message':'failed'})
            # return redirect('/managerList')
    return redirect(url_for('auth_render'))

@app.route('/manager', methods = ['POST', 'GET'])
def manager_render():
        # fields = request.args.get("ph")
        if 'verno' in session:
            cursor = mysql.connection.cursor()
            cursor.execute("select CONCAT_WS( ', ', ty_gn_hy1,ty_gn_hy2,ty_gn_hy3,ty_gn_hywal,ty_gn_hy4,ty_gn_hy5,ty_gn_hy6,ty_of_hy7 ), phn,name,address, contact_no, language, CONCAT_WS( ', ', ty_gn,ty_dr,ty_fl,ty_wal,ty_wel,ty_cnc,ty_wh,ty_of ),pref_loc from users") 

            data = cursor.fetchall() #data from database 
            print(data)
            mysql.connection.commit()
            cursor.close()
            return render_template("manager_portal.html", value=data)
        return redirect(url_for('auth_render')) 

@app.route('/auth', methods = ['POST', 'GET'])
def auth_render():
        return render_template('app.html')


# def exist_user(id_token):
#     decoded_token = auth.verify_id_token(id_token)
#     uid = decoded_token['uid']
## phone number of admin line 105
@app.route('/token', methods = ['POST', 'GET'])
def firebaseFunction():
    if request.method == 'POST':
        id_token=request.form['authentication_key']
        decoded_token = auth.verify_id_token(id_token)
        decoded_token = decoded_token['phone_number'][1:]
        session.permanent = True
        session['verno'] = decoded_token
        if(decoded_token=='19876543210'):
            return json.dumps({"url": 'admin'})
        ###
        # md = "select role from managers "
        # print(cmd)
        # cursor = mysql.connection.cursor()
        # cursor.execute(cmd)
        # data = cursor.fetchall()   
        # mysql.connection.commit()
        # cursor.close()
        ###
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM managers where phone=%s''',(decoded_token,))
        data1 = cursor.fetchall()
        print("decoded token",decoded_token)
        print(data1)
        if(data1):
            return json.dumps({"url":'manager'})
        mysql.connection.commit()
        cursor.close()

        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM users where phn=%s''',(decoded_token,))
        data = cursor.fetchall()
        print(data)
        mysql.connection.commit()
        cursor.close()
        # check uid with db
        if(data):
            # return render_template('existing.html',data = data)
            return json.dumps({"url":'exi?ph='+decoded_token})
        else:
            # return render_template('registration.html')
            return json.dumps({"url":'reg?ph='+decoded_token})
        
        # return render_template('user_login.html')
@app.route('/managersavedata', methods=['POST'])
def upload_manager_data():
    if "verno" in session and session['verno'] == "19876543210":
        try:
            name = request.form['manager_name']
            ph_no = request.form["manager_phone"]
            role = request.form["manager_role"]
            if name != "" and ph_no != "" and role != "":
                cursor = mysql.connection.cursor()
                cursor.execute(''' INSERT INTO managers(name, phone, role) VALUES(%s,%s,%s)''',(name,ph_no,role))
                
                mysql.connection.commit()
                cursor.close()
            # print("manager_data==>",name,ph_no,role)
            # return jsonify({'status':200,'message':'success'})
            return redirect('/admin')
        except Exception as e:
            print(e)
            # return jsonify({'status':404,'message':'Cannot talk to database'})
            return redirect('/admin')
    return redirect(url_for('auth_render'))

@app.route('/savedata', methods=['POST'])
def upload_files():
    if "verno" in session:
        try:
            full_name = request.form['fullname']
            address = request.form["address"]
            ph_no = request.form["phone"]
            ph_no_key = request.form["ph_no"]
            dob = request.form["dateOfBirth"]
            email = request.form["email"]
            gender = request.form["gender"]
            lang = request.form["language"]
            prev_em = request.form["employer_name"]
            year_of_job = request.form["employeedYears"]
            job_add = request.form["employer_address"]
            jobNature = request.form["work_nature"]
            typeGeneral = request.form["typeGeneral"]
            typeGeneralhistory = request.form["typeGeneralhistory"]
            typeDriving = request.form["typeDriving"]
            typeGeneralhistory1 = request.form["typeGeneralhistory1"] #typeGeneralhistory1
            # # # typeForklift = request.form["typeForklift"]
            # # # typeGeneralhistory2 = request.form["typeGeneralhistory2"]
            typeForklift = "forklift_sub"
            typeGeneralhistory2 = '0'
            typeWalkie = request.form["typeWalkie"]
            typeGeneralhistory3 = request.form["typeGeneralhistory3"]
            typeWelder = request.form["typeWelder"]
            typeGeneralhistory4 = request.form["typeGeneralhistory4"]
            typeCNC = request.form["typeCNC"]
            typeGeneralhistory5 = request.form["typeGeneralhistory5"]
            typeWarehouse = request.form["typeWarehouse"]
            typeGeneralhistory6 = request.form["typeGeneralhistory6"]
            typeOffice = request.form["typeOffice"]
            typeOfficehistory7 = request.form["typeOfficehistory7"]
            pref_location = request.form["Preferredlocation"]
            print(full_name,address,ph_no,email,dob,gender,lang,prev_em,year_of_job,job_add,jobNature,typeGeneral,typeGeneralhistory1)
            print(typeDriving,typeGeneralhistory1,typeForklift,typeGeneralhistory2,typeWalkie,typeGeneralhistory3,typeWelder,typeGeneralhistory4,typeCNC,typeGeneralhistory5,typeWarehouse,typeGeneralhistory6,typeOffice,typeOfficehistory7)
            print(pref_location)
            
        except Exception as e:
            print(e)
            return f'At the moment cannot talk to server'
        try:    
            uploaded_file = request.files['cv_doc']
            upload_id = request.files['id_doc']
            filename = secure_filename(uploaded_file.filename)
            filename_id = secure_filename(upload_id.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    return f'file type not supported'
                    # abort(400)
                filename = '.'+filename.split('.')[1]
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], ph_no_key+'cv'+filename))
            if uploaded_file:
                # return f'File uploaded successfully'
                if filename_id != '':
                    file_ext = os.path.splitext(filename_id)[1]
                    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                        return f'file type not supported'
                    # abort(400)
                    filename_id = '.'+filename_id.split(".")[1]
                    upload_id.save(os.path.join(app.config['UPLOAD_PATH'], ph_no_key+'id'+filename_id))
                if upload_id:
                    cursor = mysql.connection.cursor()
                    cursor.execute(''' INSERT INTO users(phn, name, address, dob, email, gender, language, prv_em, year_of_job, job_add, jobnature, ty_gn, ty_gn_hy1, ty_dr, ty_gn_hy2, ty_fl, ty_gn_hy3, ty_wal, ty_gn_hywal, ty_wel, ty_gn_hy4, ty_cnc, ty_gn_hy5, ty_wh, ty_gn_hy6, ty_of, ty_of_hy7, contact_no, pref_loc) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(ph_no_key,full_name,address,dob,email,gender,lang,prev_em,year_of_job,job_add,jobNature,typeGeneral,typeGeneralhistory,typeDriving,typeGeneralhistory1,typeForklift,typeGeneralhistory2,typeWalkie,typeGeneralhistory3,typeWelder,typeGeneralhistory4,typeCNC,typeGeneralhistory5,typeWarehouse,typeGeneralhistory6,typeOffice,typeOfficehistory7,ph_no, pref_location))
                    
                    mysql.connection.commit()
                    cursor.close()
                    # return f'Files uploaded successfully'
                    print(ph_no_key)
                    return redirect(('/exi?ph='+ph_no_key))
                else:
                    return f'please upload all required files'
            else:
                return f'No resume is selected' 
            
        except Exception as e:
            print("this is the exception",e)
            return f'Error encountered while uploading documents'
    return redirect(url_for('auth_render'))

@app.route('/editsavedata', methods=['POST'])
def edit_upload_files():
    if 'verno' in session:
        try:
            full_name = request.form['fullname']
            address = request.form["address"]
            ph_no = request.form["phone"]
            ph_no_key = request.form["ph_no"]
            dob = request.form["dateOfBirth"]
            email = request.form["email"]
            gender = request.form["gender"]
            lang = request.form["language"]
            prev_em = request.form["employer_name"]
            year_of_job = request.form["employeedYears"]
            job_add = request.form["employer_address"]
            jobNature = request.form["work_nature"]
            typeGeneral = request.form["typeGeneral"]
            typeGeneralhistory = request.form["typeGeneralhistory"]
            typeDriving = request.form["typeDriving"]
            typeGeneralhistory1 = request.form["typeGeneralhistory1"]
            # # typeForklift = request.form["typeForklift"]
            # typeGeneralhistory2 = request.form["typeGeneralhistory2"]
            typeForklift = "sdfsdf"
            typeGeneralhistory2 = '4'
            typeWalkie = request.form["typeWalkie"]
            typeGeneralhistory3 = request.form["typeGeneralhistory3"]
            typeWelder = request.form["typeWelder"]
            typeGeneralhistory4 = request.form["typeGeneralhistory4"]
            typeCNC = request.form["typeCNC"]
            typeGeneralhistory5 = request.form["typeGeneralhistory5"]
            typeWarehouse = request.form["typeWarehouse"]
            typeGeneralhistory6 = request.form["typeGeneralhistory6"]
            typeOffice = request.form["typeOffice"]
            typeOfficehistory7 = request.form["typeOfficehistory7"]
            pref_location = request.form["Preferredlocation"]
            # print(full_name,address,ph_no,email,dob,gender,lang,prev_em,year_of_job,job_add,jobNature,typeGeneral,typeGeneralhistory1)
            # print(typeDriving,typeGeneralhistory1,typeForklift,typeGeneralhistory2,typeWalkie,typeGeneralhistory3,typeWelder,typeGeneralhistory4,typeCNC,typeGeneralhistory5,typeWarehouse,typeGeneralhistory6,typeOffice,typeOfficehistory7)
        except Exception as e:
            print(e)
            return f'At the moment cannot talk to server'
        try:    
            uploaded_file = request.files['cv_doc']
            upload_id = request.files['id_doc']
            filename = secure_filename(uploaded_file.filename)
            filename_id = secure_filename(upload_id.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    return f'file type not supported'
                    # abort(400)
                filename = '.' + filename.split('.')[1]
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], ph_no_key+'cv'+filename))
            if uploaded_file:
                # return f'File uploaded successfully'
                if filename_id != '':
                    file_ext = os.path.splitext(filename_id)[1]
                    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                        return f'file type not supported'
                    # abort(400)
                    filename_id = '.'+filename_id.split('.')[1]
                    upload_id.save(os.path.join(app.config['UPLOAD_PATH'], ph_no_key+'id'+filename_id))
                if upload_id:
                    # cursor = mysql.connection.cursor()
                    # cmd = "UPDATE users SET name='"+full_name+"', address='"+address+"', dob='"+dob+"', email='"+email+"', gender='"+ gender+"', language='"+ lang+"', prv_em='"+ prev_em+"', year_of_job='"+year_of_job+"',job_add='"+job_add+"', jobnature='"+jobNature+"', ty_gn='"+typeGeneral+"', ty_gn_hy1='"+typeGeneralhistory +"', ty_dr='"+typeDriving+"',ty_gn_hy2='"+ typeGeneralhistory1+"', ty_fl='"+ typeForklift+"', ty_gn_hy3='"+ typeGeneralhistory2+"',ty_wal='"+ typeWalkie+"', ty_gn_hywal='"+ typeGeneralhistory3+"',ty_wel='"+typeWelder+"',ty_gn_hy4='"+typeGeneralhistory4 +"', ty_cnc='"+ typeCNC+"', ty_gn_hy5='"+typeGeneralhistory5 +"', ty_wh='"+typeWarehouse +"', ty_gn_hy6='"+ typeGeneralhistory6+"',ty_of='"+typeOffice+"', ty_of_hy7='"+ typeOfficehistory7+"', contact_no='"+ph_no+"'" +", pref_loc='"+pref_location +"' WHERE phn=" +ph_no_key
                    # print(cmd)
                    # cursor.execute(cmd)
                    # mysql.connection.commit()
                    # cursor.close()
                    # return f'Files uploaded successfully'
                    pass
                else:
                    # return f'please upload all required files'
                    pass
            else:
                # return f'No resume is selected' 
                pass
            cursor = mysql.connection.cursor()
            cmd = "UPDATE users SET name='"+full_name+"', address='"+address+"', dob='"+dob+"', email='"+email+"', gender='"+ gender+"', language='"+ lang+"', prv_em='"+ prev_em+"', year_of_job='"+year_of_job+"',job_add='"+job_add+"', jobnature='"+jobNature+"', ty_gn='"+typeGeneral+"', ty_gn_hy1='"+typeGeneralhistory +"', ty_dr='"+typeDriving+"',ty_gn_hy2='"+ typeGeneralhistory1+"', ty_fl='"+ typeForklift+"', ty_gn_hy3='"+ typeGeneralhistory2+"',ty_wal='"+ typeWalkie+"', ty_gn_hywal='"+ typeGeneralhistory3+"',ty_wel='"+typeWelder+"',ty_gn_hy4='"+typeGeneralhistory4 +"', ty_cnc='"+ typeCNC+"', ty_gn_hy5='"+typeGeneralhistory5 +"', ty_wh='"+typeWarehouse +"', ty_gn_hy6='"+ typeGeneralhistory6+"',ty_of='"+typeOffice+"', ty_of_hy7='"+ typeOfficehistory7+"', contact_no='"+ph_no+"'" +", pref_loc='"+pref_location +"' WHERE phn=" +ph_no_key
            print(cmd)
            cursor.execute(cmd)
            mysql.connection.commit()
            cursor.close()
            return redirect(request.referrer)
            
        except Exception as e:
            print(e)
            return f'Error encountered while uploading documents'
    return redirect(url_for('auth_render'))

@app.route("/index")
def registeration():
    return render_template('index.html')

@app.route("/reg")
def register():
    ph_no = request.args.get("ph")
    # return render_template('registration.html',ph_no=ph_no)
    if "verno" in session:
        if session['verno']==ph_no or session['verno']=="19876543210":
            return render_template('registration.html',ph_no=ph_no)
        return redirect('/404')
    return redirect(url_for('auth_render'))

@app.route("/exi")
def existing():
    # ph_no = request.args.get("ph")
    # cursor = mysql.connection.cursor()
    # cursor.execute(''' select * from users where phn= %s ''',(ph_no,))
    # data = cursor.fetchall()
    # print(data)   
    # mysql.connection.commit()
    # cursor.close()
    # return render_template('existing.html',data=data,ph_on=ph_no)
    ph_no = request.args.get("ph")
    if "verno" in session:
        if session['verno'] == ph_no or session['verno'] == '19876543210':
            cursor = mysql.connection.cursor()
            cursor.execute(''' select * from users where phn= %s''',(ph_no,))
            data = cursor.fetchall()
            print(data)   
            mysql.connection.commit()
            cursor.close()
            return render_template('existing.html',data=data,ph_on=ph_no)
        return redirect('/404')
    return redirect(url_for('auth_render'))

@app.route('/download')
def downloadfile():
    datavalue = request.args.get('type')
    ph = request.args.get('ph')
    return send_file('upload/'+ph+datavalue+'.pdf')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    # return render_template_string('PageNotFound {{ errorCode }}', errorCode='404'), 404
    return render_template_string('''<!doctype html>
<html>
    <head>
        <link rel="stylesheet" href="css url"/>
    </head>
    <style>
    *{
    transition: all 0.6s;
    }

    html {
        height: 100%;
    }

    body{
        font-family: 'Lato', sans-serif;
        color: #888;
        margin: 0;
    }

    #main{
        display: table;
        width: 100%;
        height: 100vh;
        text-align: center;
    }

    .fof{
        display: table-cell;
        vertical-align: middle;
    }

    .fof h1{
        font-size: 50px;
        display: inline-block;
        padding-right: 12px;
        animation: type .5s alternate infinite;
    }

    @keyframes type{
        from{box-shadow: inset -3px 0px 0px #888;}
        to{box-shadow: inset -3px 0px 0px transparent;}
    }
    </style>
    <body>
        <div id="main">
    	<div class="fof">
        		<h1>Error 404</h1>
    	</div>
</div>
    </body>
</html>
'''), 404


# headings=("Name","Address","Phone Number","Preferred Language","Job Candidate is looking for")
data=()
@app.route('/data')
def example(): 
    cursor = mysql.connection.cursor()
    cursor.execute("select * from users") 
    data = cursor.fetchall() #data from database 
    return render_template("admin_portal.html", value=data) 

@app.route('/getcusdata',methods=["POST"])
def getcusdata():
    if 'verno' in session and session['verno'] == '19876543210':
        try:
            if request.method == "POST":
                qtc_data = request.get_json()  
                lang = "" if qtc_data['language']=="All" else " language='" + qtc_data['language']+"'"
                if qtc_data['job'] == "All":
                    if lang == "":
                        cmd = "select CONCAT_WS( ', ', ty_gn_hy1,ty_gn_hy2,ty_gn_hy3,ty_gn_hywal,ty_gn_hy4,ty_gn_hy5,ty_gn_hy6,ty_of_hy7 ), phn, pref_loc, name, address, contact_no, language, CONCAT_WS( ', ', ty_gn,ty_dr,ty_fl,ty_wal,ty_wel,ty_cnc,ty_wh,ty_of ) from users"
                    else:
                        cmd = "select CONCAT_WS( ', ', ty_gn_hy1,ty_gn_hy2,ty_gn_hy3,ty_gn_hywal,ty_gn_hy4,ty_gn_hy5,ty_gn_hy6,ty_of_hy7 ), phn, pref_loc, name, address, contact_no, language, CONCAT_WS( ', ', ty_gn,ty_dr,ty_fl,ty_wal,ty_wel,ty_cnc,ty_wh,ty_of ) from users where"+ lang
                else:   
                    exp_type = globals.exp_type[qtc_data['job']] + ','
                    print(exp_type)
                    if qtc_data['sjob']=='All':
                        sjobc = ""
                        exp_val = ""
                        # jobc = ", CONCAT_WS( ', ', ty_gn,ty_dr,ty_fl,ty_wal,ty_wel,ty_cnc,ty_wh,ty_of )"
                        jobc = ", " + globals.job_type[qtc_data['job']]
                        if lang != "":
                            lang = "where " + lang + " and " + globals.job_type[qtc_data['job']] + " IS NOT NULL"
                        else:
                            lang = "where " + globals.job_type[qtc_data['job']] + " IS NOT NULL"
                    else:
                        if qtc_data['Exp'] != "": 
                            exp_val = "and " + globals.exp_type[qtc_data['job']]+ ">="+qtc_data['Exp']
                        else:
                            exp_val = ""
                        # print( globals.exp_type[qtc_data['job']]+">="+str(qtc_data['Exp']))
                        jobc = ', '+globals.job_type[qtc_data['job']]
                        sjobc = "where "+globals.job_type[qtc_data['job']]+"='"+qtc_data['sjob']+"'"
                        if lang != "":
                            lang = " and " + lang
                        
                        # loc = qtc_data['location'] if qtc_data['location'] else None # currently no field with name location exist in DB

                    cmd = "select " + exp_type +" phn, pref_loc, name, address, contact_no, language "+jobc+" from users "+sjobc+lang+exp_val
                print(cmd)
                cursor = mysql.connection.cursor()
                cursor.execute(cmd)
                data = cursor.fetchall()   
                mysql.connection.commit()
                cursor.close()
                return jsonify({'status':200,'message':'success','data':data})
        
        except Exception as e:
            print(e)        
            return jsonify({'status':404,'message':'Cannot talk to database'})
    return redirect(url_for('auth_render'))

@app.route('/logout',methods=['GET'])
def logout():
    if 'verno' in session and session['verno'] == "19876543210":
        session.pop('verno')
        return redirect(url_for('welcome'))
    return redirect(url_for('auth_render'))

@app.route('/getmandata',methods=["POST"])
def getmandata():
    try:
        if request.method == "POST":
            qtc_data = request.get_json()  
            
            cmd = "select * from managers "
            print("maangers",cmd)
            cursor = mysql.connection.cursor()
            cursor.execute(cmd)
            data = cursor.fetchall()   
            mysql.connection.commit()
            cursor.close()
            return jsonify({'status':200,'message':'success','data':data})
    
    except Exception as e:
        print(e)        
        return jsonify({'status':404,'message':'Cannot talk to database'})

if __name__=="__main__":
    app.run(debug=True, host='localhost', port=5)