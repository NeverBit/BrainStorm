import click
import datetime as dt
import json
import requests
import sys
import traceback


def get_response_or_quit(url):
    try:
        resp = requests.get(url)
    except Exception:
        click.echo('Failed to retreive content from API server.')
        sys.exit(1)
    if resp.status_code != 200:
        click.echo(f'API server returned error code {resp.status_code}')
        sys.exit(1)
    return resp


@click.group()
def main():
    pass


@main.command(name='get-users')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=5000)
def get_users(host, port):
    resp = get_response_or_quit(f'http://{host}:{port}/users')
    users = json.loads(resp.content)
    if not users:
        click.echo(f'No users found.')
        sys.exit(0)

    click.echo(f'Users\' IDs & names:')
    for uid in users:
        click.echo(f'[{uid}] {users[uid]}')


@main.command(name='get-user')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=5000)
@click.argument('uid', type=int)
def get_user(host, port, uid):
    resp = get_response_or_quit(f'http://{host}:{port}/users/{uid}')
    fields = json.loads(resp.content)

    # Format birthday
    ticks_as_dt = dt.datetime.fromtimestamp(fields['birthday'])
    fields['birthday'] = ticks_as_dt.strftime("%Y-%m-%d")

    click.echo(f'User Info:')
    for field in fields:
        click.echo(f'{field}: {fields[field]}')


@main.command(name='get-snapshots')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=5000)
@click.argument('uid', type=int)
def get_snapshots(host, port, uid):
    resp = get_response_or_quit(f'http://{host}:{port}/users/{uid}/snapshots')
    snaps = json.loads(resp.content)

    click.echo(f'Snapshots:')
    for snap_id in snaps:
        fields = snaps[snap_id]
        ticks_as_dt = dt.datetime.fromtimestamp(fields["datetime"] / 1000.0)
        snaptime = ticks_as_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        click.echo(f'{snap_id}: {snaptime}')


@main.command(name='get-snapshot')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=5000)
@click.argument('uid', type=int)
@click.argument('snap_id', type=int)
def get_snapshot(host, port, uid, snap_id):
    url = f'http://{host}:{port}/users/{uid}/snapshots/{snap_id}'
    resp = get_response_or_quit(url)
    fields = json.loads(resp.content)

    click.echo(f'Snapshot Info:')
    click.echo(f'id: {fields["id"]}')

    ticks_as_dt = dt.datetime.fromtimestamp(fields["datetime"] / 1000.0)
    snaptime = ticks_as_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    click.echo(f'datetime: {snaptime}')

    results = json.loads(fields["available_results"])
    click.echo(f'available_results:')
    for result in results:
        click.echo(f'\t{result}')


@main.command(name='get-result')
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=str, default=5000)
@click.argument('uid', type=int)
@click.argument('snap_id', type=int)
@click.argument('parser', type=str)
def get_result(host, port, uid, snap_id, parser):
    url = f'http://{host}:{port}/users/{uid}/snapshots/{snap_id}/{parser}'
    resp = get_response_or_quit(url)
    fields = json.loads(resp.content)

    click.echo(f'Result Info:')
    for field in fields:
        click.echo(f'{field}: {fields[field]}')


if __name__ == '__main__':
    try:
        main(prog_name='BrainStorm.cli', obj={})
    except Exception as error:
        print(f'ERROR: {error}')
        track = traceback.format_exc()
        print(track)
        sys.exit(1)
