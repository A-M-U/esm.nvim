import pynvim
import yaml
import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from esm_element import EsmElementFactory

@pynvim.plugin
class Esm(object):
    current_element = None

    def __init__(self, vim):
        self.vim = vim


    @pynvim.command('EsmRev', range='', nargs='*',sync=True)
    def esm_change_rev(self, args, range):

        self.__esm_set_current_element()
        self.current_element.update_revision()
        self.__esm_update_current_element_in_active_buffer()


    @pynvim.command('EsmChangeUrl', range='', nargs='*',sync=True)
    def esm_change_url(self, args, range):
        branch_type = args[0]

        self.__esm_set_current_element()

        if branch_type == 'trunk':
            url_prefix, url_suffix = self.current_element.get_splitted_url_list_by_branch_type()
            self.current_element.url = url_prefix + r'/trunk/' + url_suffix
            self.current_element.update_revision()
            self.__esm_update_current_element_in_active_buffer()
            return
        elif branch_type == 'tags':
            display_list = self.current_element.get_url_list('tags')
            display_list.reverse()
        elif branch_type == 'branches':
            display_list = self.current_element.get_url_list('branches')
        else:
            raise AssertionError('branch_type {} not supported'.format(branch_type))

        scratch_buffer = self.vim.api.create_buf(False, True)
        self.__esm_open_window_with_enter_selection(scratch_buffer, display_list, branch_type)


    @pynvim.command('EsmCmd', range='', nargs='*',sync=True)
    def esm_cmd(self, args, range):
        esm_command = args[0]

        self.__esm_set_current_element()

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


    @pynvim.command('EsmEnter', range='', nargs='*',sync=True)
    def __esm_keymap_enter_selection(self, args, range):
        branch_type = args[0]
        current_word = self.vim.eval('expand("<cWORD>")')

        url_prefix, url_suffix = self.current_element.get_splitted_url_list_by_branch_type()

        self.current_element.url = url_prefix + r'/' + branch_type + r'/' + current_word + url_suffix
        self.vim.api.win_close(0, True)
        self.current_element.update_revision()
        self.__esm_update_current_element_in_active_buffer()


    @pynvim.command('EsmClose', range='', nargs='*',sync=True)
    def esm_close_win(self, args, range):
        self.vim.api.win_close(0, True)


    def __esm_update_current_element_in_active_buffer(self):
        """ takes esm_element object """
        row, column = self.vim.api.win_get_cursor(0)
        start = row-1
        end = row+2
        esm_element_buffer_lines = self.vim.api.buf_get_lines(0, start, end, 0)

        for i in range(len(esm_element_buffer_lines)):
            # stop splitting after first ':' for not breaking the url string
            split_line = esm_element_buffer_lines[i].split(':', 1)
            if split_line[0].strip() == 'url':
                split_line[1] = ' ' + self.current_element.url
            elif split_line[0].strip() == 'revision':
                split_line[1] = ' ' + str(self.current_element.revision)

            esm_element_buffer_lines[i] = ':'.join(split_line)

        self.vim.api.buf_set_lines(0, start, end, 0, esm_element_buffer_lines)


    @staticmethod
    def __esm_get_window_size_for_list(display_list):
        width = 0
        heigth = len(display_list)

        for e in display_list:
            if len(e) > width:
                width = len(e)

        return (width + 2, heigth + 1)


    def __esm_open_window_with_enter_selection(self, buf, display_list, branch_type):
        width, heigth = self.__esm_get_window_size_for_list(display_list)
        self.vim.api.buf_set_lines(buf, 0, -1, True, display_list)
        opts = {'relative': 'cursor', 'width': width, 'height': heigth, 'col': 0, 'row': 1, 'anchor': 'NW', 'style': 'minimal'}

        mappings = { '<cr>': ':EsmEnter ' + branch_type + '<cr>',
                        'q': ':EsmClose<cr>'}
        for k, v in mappings.items():
            self.vim.api.buf_set_keymap(buf, 'n', k, v, {'nowait':True, 'noremap' : True, 'silent' : True })

        self.vim.command('autocmd BufLeave <buffer=' + str(buf.number) + '> close')

        win = self.vim.api.open_win(buf, 1, opts)

        return win

    def __esm_set_current_element(self):
        current_word = (self.vim.eval('expand("<cWORD>")')).strip(':')
        current_file_path = self.vim.eval('expand("%:p")')

        with open(current_file_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.current_element = EsmElementFactory.get_element(data, current_word)

