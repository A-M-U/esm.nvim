import pynvim
import yaml
import os

@pynvim.plugin
class Esm(object):
    found_list = []

    def __init__(self, vim):
        self.vim = vim

    def esm_find_key(self, dictionary, keyword):
        for k, v in dictionary.items():
            if k == keyword:
                self.found_list.append(k)
                return True
            if isinstance(v, dict):
                if self.esm_find_key(v, keyword):
                    self.found_list.append(k)
                    return True
            else:
                if k == keyword:
                    self.found_list.append(k)
                    return True
        return False


    @pynvim.command('EsmUpdate', range='', nargs='*',sync=True)
    def esm_up(self, args, range):
        current_word = self.vim.eval('expand("<cword>")')
        current_file_path = self.vim.eval('expand("%:p")')
    
        with open(current_file_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            
            if self.esm_find_key(data, current_word):
                path = "\""
                for i in self.found_list:
                    path = path + str(i) + '/'
                path = path + "\""

                scratch_buffer = self.vim.api.create_buf(False, True)
                win = self.esm_open_window(scratch_buffer)
                self.esm_mappings(scratch_buffer, path)

    # @pynvim.command('EsmCmd', range='', nargs='*',sync=True)
    # def esmCmd(self, args, range):
    #     scratch_buffer = self.vim.api.create_buf(False, True)
    #     win = self.esm_open_window(scratch_buffer)
    #     self.esm_mappings(scratch_buffer)

    @pynvim.function('EsmClose')
    def esm_close_win(self, args):
        self.vim.api.win_close(0, True)


    def esm_open_window(self, buf):
        opts = {'relative': 'cursor', 'width': 10, 'height': 2, 'col': 0, 'row': 1, 'anchor': 'NW', 'style': 'minimal'}
        self.vim.api.buf_set_lines(buf, 0, -1, True, ["blub", "text"])
        win = self.vim.api.open_win(buf, 1, opts)


    def esm_mappings(self, buf, path):
        mappings = {
                'e' : ':echo "element ' + path + '"<cr>',
                'f' : ':echo "file ' + path + '"<cr>',
                'g' : ':echo "group ' + path + '"<cr>',
                'q' : ':exec EsmClose()<cr>',
                '<cr>': ':exec EsmClose()<cr>'}

        for k, v in mappings.items():
            self.vim.api.buf_set_keymap(buf, 'n', k, v, {'nowait':True, 'noremap' : True, 'silent' : True })


