from flask import Flask, session, redirect, url_for, escape, request
from flask.ext.restful import reqparse, abort, Api, Resource
import __builtin__

app = Flask(__name__)
api = Api(app)

@api.representation('json')
def json(data, code, headers):
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers)
    return resp

__builtin__.verbose = None

@app.route('/')
def index():
    if 'username' in session:
        app.logger.debug('A user just got authenticated')
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
        '''    

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr97j/3yX R~XHH!jmN]LWX/,?RT'

#THIS IS JUST A SAMPLE
DATA = {
    '20130201' : { '37484' : {'java' : 364, 'c' : 434}},
    '20120524' : { '345' : {'java' : 324, 'c' : 134}},
    '20120521' : { '345' : {'.net' : 24, 'asm' : 134}},
}

def abort_if_behav_doesnt_exist(entryid):
    if entryid not in DATA:
        abort(404, message="GitJob in data {} doesn't exist".format(entryid))

parser = reqparse.RequestParser()
parser.add_argument('skill-load', type=str)

#  show a single behav data item and lets you delete them
class GitJob(Resource):
    def get(self, entryid):
        abort_if_behav_doesnt_exist(entryid)
        return DATA[entryid]

    def delete(self, entryid):
        abort_if_behav_doesnt_exist(entryid)
        del DATA[entryid]
        return '', 204

    def put(self, entryid, taskid):
        args = parser.parse_args()
        bd = json.dumps(args['skill-load'])
        DATA[entryid][taskid] = bd
        return entryid, 201


# BehavDataList
# shows a list of all todos, and lets you POST to add new behav data
class GitJobList(Resource):
    def get(self):
        print 'get(self) running nicely..'
        return DATA

##
## Actually setup the Api resource routing here
##
api.add_resource(GitJobList, '/gitjob')
api.add_resource(GitJob, '/gitjob/<string:taskid>:<string:skillid>')

if __name__ == '__main__':
    app.run(debug=True)
