import click
import datetime
from . import db_access
from .db_access import Reader
import flask
from .image import image
import importlib
import jinja2
import json
import mimetypes
import os
from pathlib import Path
import pika
from .proto import Snapshot, SnapshotSlim
import sys
import traceback


app = flask.Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
serverInst = None


class WebServer:
    def __init__(self, database_url):
        self.reader = Reader(database_url)

    def get_home_page(self):
        ''' Returns the home page '''
        return flask.render_template('home.html')

    def get_static_res(self, res_name):
        ''' Returns one of the static resources files'''
        return flask.send_from_directory('static_resources', res_name)

    def get_users_page(self):
        ''' Returns all users page '''
        users = self.reader.get_users()
        return flask.render_template('users.html', users=users)

    def get_user_page(self, uid):
        ''' Returns a user's page '''
        user = self.reader.get_user(uid)
        if not user:
            flask.abort(404)
        snapshots = self.reader.get_snapshots_by_user(uid)
        converted_ticks = datetime.datetime.fromtimestamp(user['birthday'])
        user['birthday'] = converted_ticks.strftime("%Y-%m-%d")
        return flask.render_template('user.html', user=user,
                                     snapshots=snapshots)

    def get_snapshot_parseres_results(self,uid, snapshot_id, available_results):
        '''
        Returns a list of HTML components - one for every parser reasult
        available for the snashot
        '''
        results_htmls = []
        for result_name in available_results:
            # Compose the right parser template URI
            plugin_templat_path = f'results_plugins/{result_name}.html'

            # Read parser results from the DB
            result_json = self.reader.get_parser_res(result_name, snapshot_id)
            result_dict = json.loads(result_json)

            # Render the parser result HTML component
            try:
                # Assuming the parser have a specified generator 'plugin' template
                result_html = flask.render_template(plugin_templat_path,
                                                    user_id=uid,
                                                    snapshot_id=snapshot_id,
                                                    result_name=result_name,
                                                    res_json=result_json,
                                                    res_dict=result_dict)
                is_raw_results = False
            except jinja2.exceptions.TemplateNotFound:
                # Catching this exceptions tells us a specific plugin does not exist.
                # Because we still want to show the the result we use the
                # default template (shows the result as a JSON) 
                result_html = flask.render_template('results_plugins/default.html',
                                                    user_id=uid,
                                                    snapshot_id=snapshot_id,
                                                    result_name=result_name,
                                                    res_json=result_json,
                                                    res_dict=result_dict)
                is_raw_results = True
            # Append to the output list
            results_htmls.append({'result_name':result_name,'is_raw':is_raw_results,'result_html':result_html})
        return results_htmls

    def get_snapshot_content(self, uid, snapshot_id):
        ''' Returns a snapshot's page content ) parsers results '''
        # Assert the user exists in the DB
        user = self.reader.get_user(uid)
        if not user:
            flask.abort(404)

        # Get the snapshot data from the DB
        snapshot = self.reader.get_snapshot(uid, snapshot_id)
        if not snapshot:
            flask.abort(404)

        # Parser datetime to humand-readable format
        dtime_ms = snapshot['datetime']
        converted_ticks = datetime.datetime.fromtimestamp(dtime_ms/1000.0)
        snapshot['datetime'] = converted_ticks.strftime("%Y-%m-%d %H:%M:%S")

        # Get available results names from the snapshot info 
        results = json.loads(snapshot['available_results'])
        
        # Render HTML components for the different parsers' results
        results_htmls = self.get_snapshot_parseres_results(uid,
                                                           snapshot_id,
                                                           results)
        final_html = ''
        for res_dict in results_htmls:
            final_html += res_dict['result_html']
        
        
        return flask.render_template('snapshot_parsers_results.html',
                                     results_htmls=results_htmls)

    def get_snapshot_page(self, uid, snapshot_id):
        ''' Returns a snapshot's page '''
        # Assert the user exists in the DB
        user = self.reader.get_user(uid)
        if not user:
            flask.abort(404)

        # Get the snapshot data from the DB
        snapshot = self.reader.get_snapshot(uid, snapshot_id)
        if not snapshot:
            flask.abort(404)

        # Parser datetime to humand-readable format
        dtime_ms = snapshot['datetime']
        converted_ticks = datetime.datetime.fromtimestamp(dtime_ms/1000.0)
        snapshot['datetime'] = converted_ticks.strftime("%Y-%m-%d %H:%M:%S")

        # Get available results names from the snapshot info 
        results = json.loads(snapshot['available_results'])
        
        # Render HTML components for the different parsers' results
        results_htmls = self.get_snapshot_parseres_results(uid,
                                                           snapshot_id,
                                                           results)

        return flask.render_template('snapshot.html', user=user,
                                     snapshot=snapshot,
                                     results_htmls=results_htmls)

    def get_user_snapshot_timeline(self, uid):
        ''' Returns summary of the user's snapshots as an HTML '''
        user = self.reader.get_user(uid)
        if not user:
            flask.abort(404)

        converted_ticks = datetime.datetime.fromtimestamp(user['birthday'])
        user['birthday'] = converted_ticks.strftime("%Y-%m-%d")

        snapshots = self.reader.get_snapshots_by_user(uid)
        for snapshot_id,snapshot in snapshots.items():
            # Get available results names from the snapshot info 
            results = json.loads(snapshot['available_results'])
            
            # Render HTML components for the different parsers' results
            results_htmls = self.get_snapshot_parseres_results(uid,
                                                            snapshot_id,
                                                            results)
            
            # Expand snapshot object
            snapshot['results_htmls'] = results_htmls

        return flask.render_template('timeline_data.html', user=user,
                                     snapshots=snapshots)

    def get_result_data(self, result_name, snapshot_id):
        results = self.reader.get_parser_res(result_name, snapshot_id)
        if not results:
            # Could not find specific result/snapshot
            flask.abort(404)

        res_dict = json.loads(results)
        if 'data_path' not in res_dict:
            # The specific result type does indicate raw data is available
            flask.abort(404)

        path = res_dict['data_path']
        return flask.send_file(path)



@app.route('/')
def get_home():
    return serverInst.get_home_page()


@app.route('/static/<res_name>')
def get_static_res(res_name):
    return serverInst.get_static_res(res_name)


@app.route('/users')
def get_users_page():
    return serverInst.get_users_page()


@app.route('/users/<int:user_id>')
def get_user_page(user_id):
    return serverInst.get_user_page(user_id)


@app.route('/users/<int:user_id>/snapshots/<int:snapshot_id>', defaults={'requested_raw': False})
@app.route('/users/<int:user_id>/snapshots/<int:snapshot_id>/raw', defaults={'requested_raw': True})
def get_snapshot_page(user_id, snapshot_id, requested_raw):
    if(requested_raw):
        return serverInst.get_snapshot_content(user_id, snapshot_id)
    return serverInst.get_snapshot_page(user_id, snapshot_id)


@app.route('/users/<int:user_id>/timeline_data.html')
def get_user_snapshot_timeline(user_id):
    return serverInst.get_user_snapshot_timeline(user_id)


@app.route(
    '/users/<int:user_id>/snapshots/<int:snapshot_id>/<result_name>/data',
    methods=['GET'])
def get_result_data(user_id, snapshot_id, result_name):
    return serverInst.get_result_data(result_name, snapshot_id)


@click.group()
def main():
    pass


@main.command(name='run-server')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=8080)
@click.argument('database_url', type=str)
def run_server(host, port, database_url):
    global serverInst
    serverInst = WebServer(database_url)
    print(f' @@@ Debug run-server and serverInst is {serverInst}')

    # let flask take the reins
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.gui', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        track = traceback.format_exc()
        print(track)
        sys.exit(1)
