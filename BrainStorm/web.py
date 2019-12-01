from .website import Website
from pathlib import Path

_data_dir = None

my_website = Website()


# An integer parses which returns True/False depending on success
# and doesn't raise exceptions
def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False


@my_website.route('/')
def get_home_resp():
    global _data_dir
    header ='''<html>
                <head>
                    <title>Brain Computer Interface</title>
                </head>
                <body>
                    <ul>'''
    list_content = ''
    if(_data_dir.exists()):
        for x in _data_dir.iterdir():
            if x.is_dir():
                list_item = '<li><a href="/users/{0}">user {0}</a></li>'.format(x.name)
                list_content = list_content + list_item
    if(list_content == ''):
        list_content = 'No users found'
    footer =       '''</ul>
                </body>
            </html>'''

    resp = header+list_content+footer
    return (200,resp)



@my_website.route('/users/([0-9]+)')
def get_user_thoughts_resp(user_id):
    global _data_dir
    header = '''<html>
                  <head>
                     <title>Brain Computer Interface: User {0}</title>
                  </head>
                  <body>
                     <table>'''.format(user_id)
    table_content = ''
    user_dir = _data_dir / str(user_id)
    if(user_dir.exists()):
        for x in user_dir.iterdir():
            if not x.is_dir():
                # Get dir name without suffix (.txt), split date and time
                # fix dashes in time to ':'s
                date,time = x.stem.split("_")
                time = time.replace("-",":")
                date_time_str = f'{date} {time}' 
                with x.open() as f:
                    line = f.readline()
                    while not (line == ''):
                        table_content = table_content +'''
                                                    <tr>
                                                        <td>{0}</td>
                                                        <td>{1}</td>
                                                    </tr>'''.format(date_time_str,line)
                        line = f.readline()
    if (table_content == ''):
        table_content = '<tr><td>No thoughts found for this user<td><tr>'
    footer = '''          </table>
                    </body>
                </html>'''
    resp = header+table_content+footer
    return (200,resp)

def run_webserver(address,data_dir):
    global _data_dir
    _data_dir = Path(data_dir)
    my_website.run(address)

def main(argv):
    if len(argv) != 3:
        print(f'USAGE: {argv[0]} <address> <data_dir>') 
        return 1
    try:
        ip_port_list = argv[1].split(':')
        ip_port_tup = (ip_port_list[0],int(ip_port_list[1]))
        data_dir = argv[2] # Global
        
        run_webserver(ip_port_tup,data_dir)
    except Exception as error:
        print(f'ERROR: {error}')
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
