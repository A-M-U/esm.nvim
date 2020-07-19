import pynvim
import yaml
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from esm_element import EsmElementFactory

@pynvim.plugin
class Esm(object):
    current_element

    def __init__(self, vim):
        self.vim = vim

    @pynvim.command('EsmChangeUrl', range='', nargs='*',sync=True)
    def esm_change_url(self, args, range):
        branch_type = args[0]

        current_word = (self.vim.eval('expand("<cWORD>")')).strip(':')
        current_file_path = self.vim.eval('expand("%:p")')

        with open(current_file_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.current_element = EsmElementFactory.get_element(data, current_word)

        if branch_type == 'trunk':
            pass
        elif branch_type == 'tags':
            pass
        elif branch_type == 'branches':
            pass
        else:
            raise AssertionError('branch_type {} not supported'.format(branch_type))

        #todo: replace with correct data from functions
        test_list = ['asdfasf', 'asdlfja;sdfj;adfj;aj', 'askdflakdjflakjdflkaasdkfjadkfjlakdfjl', 'alkdf']

        scratch_buffer = self.vim.api.create_buf(False, True)
        win = self.__esm_open_window_with_enter_selection(scratch_buffer, test_list)

        self.__esm_update_current_element_in_active_buffer()


    @pynvim.command('EsmCmd', range='', nargs='*',sync=True)
    def esm_cmd(self, args, range):
        esm_command = args[0]

        current_word = (self.vim.eval('expand("<cWORD>")')).strip(':')
        current_file_path = self.vim.eval('expand("%:p")')

        with open(current_file_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.current_element = EsmElementFactory.get_element(data, current_word)

        if esm_command == 'update':
            command_str = self.current_element.get_update_command()
        elif esm_command == 'update_file':
            command_str = self.current_element.get_update_file_command()
        elif esm_command == 'diff':
            command_str = self.current_element.get_diff_command()
        elif esm_command == 'clean':
            command_str = self.current_element.get_clean_command()
        else:
            raise AssertionError('EsmCmd does not support argument: {}'.format(esm_command))

        self.vim.command(':!'+ command_str)


    def __esm_update_current_element_in_active_buffer(self):
        """ takes esm_element object """
        row, column = self.vim.api.win_get_cursor(0)
        start = row-1
        end = row+1
        esm_element_buffer_lines = self.vim.api.buf_get_lines(0, start, end, 0)

        for line in esm_element_buffer_lines:
            split_line = line.split(':')
            if split_line[0] == 'url':
                split_line[1] = self.current_element.url
            elif split_line[0] == 'revision':
                split_line[1] = self.current_element.revision

            line = ':'.join(test_line)

        self.vim.api.buf_set_lines(0, start, end, 0, lines)


    @staticmethod
    def __esm_get_window_size_for_list(display_list):
        width = 0
        heigth = len(display_list)

        for e in display_list:
            if len(e) > width:
                width = len(e)

        return (width + 2, heigth + 1)


    def __esm_open_window_with_enter_selection(self, buf, display_list):
        width, heigth = self.__esm_get_window_size_for_list(display_list)
        self.vim.api.buf_set_lines(buf, 0, -1, True, display_list)
        opts = {'relative': 'cursor', 'width': width, 'height': heigth, 'col': 0, 'row': 1, 'anchor': 'NW', 'style': 'minimal'}

        mappings = { '<cr>': ':EsmEnter<cr>',
                        'q': ':EsmClose<cr>'}
        for k, v in mappings.items():
            self.vim.api.buf_set_keymap(buf, 'n', k, v, {'nowait':True, 'noremap' : True, 'silent' : True })

        win = self.vim.api.open_win(buf, 1, opts)

        return win


    @pynvim.command('EsmEnter', range='', nargs='*',sync=True)
    def __esm_keymap_enter_selection(self, args, range):
        current_word = self.vim.eval('expand("<cWORD>")')
        #todo modify current_element
        self.vim.command(':echo "'+ current_word + '"')
        self.vim.api.win_close(0, True)


    @pynvim.function('EsmClose')
    def esm_close_win(self, args):
        self.vim.api.win_close(0, True)
