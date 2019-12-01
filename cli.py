import sys
import inspect
usage_msg = 'USAGE: python {0} <command> [<key>=<value>]*'
class CommandLineInterface:
    com_n_args = {}
    com_n_func = {}
    def command(self, f):
        f_name = f.__name__
        f_args = inspect.getfullargspec(f).args
        self.com_n_args[f_name]=f_args
        self.com_n_func[f_name]=f
        return f

    def main(self):
        args = sys.argv
        if(len(args) < 2):
            print(usage_msg.format(args[0]))
            sys.exit(-1);
        req_f_name = args[1];
        if not req_f_name in self.com_n_args:
            print(usage_msg.format(args[0]))
            print(f' ERROR: Invalid command name \'{req_f_name}\'')
            sys.exit(-1);
        req_f_args = self.com_n_args[req_f_name]
        args_dict = {}
        for arg in args[2:]:
            splitted_arg = arg.split('=',1)
            if not len(splitted_arg) == 2:
                print(usage_msg.format(args[0]))
                print(f' ERROR: Missing \'=\' in arg: \'{arg}\'')
                sys.exit(-1);
            arg_key = splitted_arg[0]
            arg_val = splitted_arg[1]
            if not arg_key in req_f_args:
                print(usage_msg.format(args[0]))
                print(f' ERROR: Unexpected argument: \'{arg_key}\'')
                sys.exit(-1);
            if arg_key in args_dict:
                print(usage_msg.format(args[0]))
                print(f' ERROR: arg key defined twice: \'{arg_key}\'')
                sys.exit(-1);
            args_dict[arg_key] = arg_val
        if not len(args_dict) == len(req_f_args):
            print(usage_msg.format(args[0]))
            print(f' ERROR: incorrect number of arguments. Expected {len(req_f_args)} got {len(args_dict)}')
            sys.exit(-1);
        req_f = self.com_n_func[req_f_name]
        req_f(**args_dict)
        sys.exit(0);
