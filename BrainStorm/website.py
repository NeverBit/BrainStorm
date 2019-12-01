import http.server
import re

def route_deco_fac(route_dict,path):
    def deco(f):
        # 'fixing' regular expressions to match entire string only
        if not path.endswith('$'):
            new_path = '^' + path + '$'
        else:
            new_path = path
        route_dict[new_path] = f
        return f
    return deco

class ReqHandlerFactory:
    def create(route_dict):
        class ReqHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                for rexp,func in route_dict.items():
                    reg_search_res =  re.search(rexp,self.path)
                    if reg_search_res: # if found match
                        res_code,body = func(*(reg_search_res.groups()))
                        self.send_response(res_code)
                        if(body):
                            resp = body.encode()
                            self.send_header('Content-Type','text/html')
                            self.send_header('Content-Length',len(resp))
                            self.end_headers()
                            self.wfile.write(resp)
                        else:
                            self.end_headers()
                        # we found a match so we break the loop to avoid the 404 at the else 
                        break;
                else:
                   # requested path not defined, returning 404 
                    self.send_response(404)
                    self.end_headers();
        return ReqHandler

class Website:
    def __init__(self):
        self.route_dict = {}
    def route(self, path):
        return route_deco_fac(self.route_dict,path); 

    def run(self, address):
        http_server = http.server.HTTPServer(address,ReqHandlerFactory.create(self.route_dict))
        http_server.serve_forever()
