from abc import ABC, abstractstaticmethod

class EsmElementFactory():
    key_list = []
    element_dict = {}

    @staticmethod
    def get_element(externals, keyword):
        try:
            if self._esm_find_key_in_dict(externals, keyword):
                key_path = "/".join(self.key_list[::-1])
                try:
                    if _esm_element_is_group(externals):
                        return EsmElementGroup(key_path, key_list[-1])
                    elif _esm_element_is_normal(externals, key_list[-1]):
                        return EsmElementNormal(key_path, key_list[-1], element_dict[key_list[-1]]['url'],
                                                element_dict[key_list[-1]]['rev'])
                    elif _esm_element_is_bsp(externals, key_list[-1]):
                        return EsmElementBsp(key_path, key_list[-1], element_dict[key_list[-1]]['url'],
                                                element_dict[key_list[-1]]['rev'])
                    raise AssertionError('element type not found')
                except AssertionError as _e:
                    print(_e)
            raise AssertionError('keyord not found in dict')
        except AssertionError as _e:
            print(_e)
    #todo: output error in vim

    def _esm_element_is_normal(self, dictionary, name):
        #todo: use regex to find the repo name
        return False

    def _esm_element_is_bsp(self, dictionary, name):
        #todo: use regex to find the repo name
        return False

    def _esm_element_is_group(self, dictionary):
        if _dict_depth(dictionary) > 1:
            return True
        return False

    def _dict_depth(self, dictionary): 
        if isinstance(dictionary, dict): 
            return 1 + (max(map(self._dict_depth, dictionary.values())) if dictionary else 0) 
        return 0

    def _esm_find_key_in_dict(self, dictionary, keyword):
        self.key_list.clear()
        self.element_dict.clear()
        for k, v in dictionary.items():
            if k == keyword:
                self.key_list.append(k)
                self.element_dict = v.copy()
                return True
            elif isinstance(v, dict):
                if self._esm_find_key_in_dict(v, keyword):
                    self.key_list.append(k)
                    return True
        return False


class EsmElementInterface(ABC):

    @abstractstaticmethod
    def get_update_command():
        """interface method"""


    @abstractstaticmethod
    def get_diff_command():
        """interface method"""

    @abstractstaticmethod
    def get_clean_command():
        """interface method"""


class EsmElementNormal(EsmElementInterface):
    def __init__(self, key_path, name, url, rev):
        self.element_type = 'normal'
        self.key_path = key_path
        self.name = name
        self.url =  url
        self.revison = rev


    def get_update_command(self):
        return _esm_command('update') 


    def get_diff_command(self):
        return _esm_command('diff') 


    def get_clean_command(self):
        return _esm_command('clean') 


    def update_revision(self, requested_revison='HEAD')
        if requested_revison == 'HEAD':
            # get svn head rev from 
        else:
            self.revison = requested_revison


    def get_branch_list(self):
        # extract brach dir from url and return list


    def get_tag_list(self):
        # extract tags dir from url and return list


    def set_url_and_update_revision(self, new_url):
        self.url = new_url
        self.update_revision()


    def _esm_command(self, command_option):
        command_str = 'svnext '+ command_option + ' --overwrite-local-changes -e ' + self.key_path
        return command_str 


class EsmElementGroup(EsmElementInterface):
    def __init__(self, key_path, name):
        self.element_type = 'group'
        self.key_path = key_path
        self.name = name


    def get_update_command(self):
        return _esm_command('update') 


    def get_diff_command(self):
        return _esm_command('diff') 


    def get_clean_command(self):
        return _esm_command('clean') 

    def _esm_command(self, command_option):
        command_str = 'svnext '+ command_option + ' --overwrite-local-changes -g ' + self.key_path
        return command_str 



class EsmElementBsp(EsmElementInterface):
    def __init__(self, key_path, name, url, rev):
        self.element_type = 'bsp'
        self.key_path = key_path
        self.name = name
        self.url =  url
        self.revison = rev


    def get_update_command(self):
        return _esm_command('update') 


    def get_diff_command(self):
        return _esm_command('diff') 


    def get_clean_command(self):
        return _esm_command('clean') 

    def _esm_command(self, command_option):
        command_str = 'svnext '+ command_option + ' --overwrite-local-changes -e ' + self.key_path
        return command_str 


