import pynvim
import yaml
import os

@pynvim.plugin
class Esm(object):
    found_list = []

    def __init__(self, vim):
        self.vim = vim

    @pynvim.command('Esm', range='', nargs='*',sync=True)
    def esm(self, args, range):
        # add checks for arg parsing
        esm_command = args[0]
        esm_command_option = args[1]

        path = self._esm_get_key_path_in_dict()
        if path is not None:
            scratch_buffer = self.vim.api.create_buf(False, True)
            win = self._esm_open_window(scratch_buffer, esm_command)
            self._esm_mappings(scratch_buffer, path, esm_command, esm_command_option)


    @pynvim.function('EsmClose')
    def esm_close_win(self, args):
        self.vim.api.win_close(0, True)


    @pynvim.command('EsmQuick', range='', nargs='*',sync=True)
    def esm_quick(self, args, range):
        # add checks for arg parsing
        esm_command = args[0]
        esm_command_option = args[1]

        path = self._esm_get_key_path_in_dict()
        if path is not None:
            self.vim.command(':!svnext ' + esm_command + ' --overwrite-local-changes -' + esm_command_option + ' ' + path)


    def _esm_get_key_path_in_dict(self):
        current_word = (self.vim.eval('expand("<cWORD>")')).strip(':')
        current_file_path = self.vim.eval('expand("%:p")')
    
        self.found_list.clear()
        with open(current_file_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            
            if self._esm_find_key_in_dict(data, current_word):
                path = "/".join(self.found_list[::-1])
        return path


    def _esm_find_key_in_dict(self, dictionary, keyword):
        for k, v in dictionary.items():
            if k == keyword:
                self.found_list.append(k)
                return True
            if isinstance(v, dict):
                if self._esm_find_key_in_dict(v, keyword):
                    self.found_list.append(k)
                    return True
            else:
                if k == keyword:
                    self.found_list.append(k)
                    return True
        return False


    def _esm_open_window(self, buf, esm_command):
        opts = {'relative': 'cursor', 'width': 20, 'height': 6, 'col': 0, 'row': 1, 'anchor': 'NW', 'style': 'minimal'}
        self.vim.api.buf_set_lines(buf, 0, -1, True, [esm_command, "=====================", 
                                                      "e: element", "g: group", "f: file", "q: quit"])
        win = self.vim.api.open_win(buf, 1, opts)


    def _esm_mappings(self, buf, path, esm_command, esm_command_option):
        # execute command under cursor if hitting enter
        mappings = {
                'e' : ':exec EsmClose()<cr>:!svnext ' + esm_command + ' --overwrite-local-changes -' + esm_command_option + ' ' + path + '<cr>',
                'g' : ':exec EsmClose()<cr>:!svnext ' + esm_command + ' --overwrite-local-changes -' + esm_command_option + ' ' + path + '<cr>',
                'f' : ':exec EsmClose()<cr>:!svnext ' + esm_command + ' --overwrite-local-changes -' + esm_command_option + ' ' + path + '<cr>',
                'q' : ':exec EsmClose()<cr>',
                '<cr>': ':exec EsmClose()<cr>'}

        for k, v in mappings.items():
            self.vim.api.buf_set_keymap(buf, 'n', k, v, {'nowait':True, 'noremap' : True, 'silent' : True })


