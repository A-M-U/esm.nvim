from abc import ABC, abstractstaticmethod

class EsmElementFactory():
    key_list = []
    element_dict = {}

    @classmethod
    def get_element(cls, externals, keyword):
        try:
            if cls._esm_find_key_in_dict(externals, keyword):
                key_path = "/".join(cls.key_list[::-1])
                try:
                    element_name = cls.key_list[-1]
                    if cls._esm_element_is_group(externals):
                        return EsmElementGroup(key_path, element_name)
                    else:
                        element_url = element_dict[cls.key_list[-1]]['url']
                        element_rev = element_dict[cls.key_list[-1]]['rev']
                        if cls._esm_element_is_normal(externals, element_name):
                            return EsmElementNormal(key_path, element_name, element_url, element_rev)
                        elif cls._esm_element_is_bsp(externals, element_name):
                            return EsmElementBsp(key_path, element_name, element_url, element_rev)
                        elif cls._esm_element_is_port(externals, element_name):
                            return EsmElementPort(key_path, element_name, element_url, element_rev)
                    raise AssertionError('element type not found')
                except AssertionError as _e:
                    print(_e)
            raise AssertionError('keyord not found in dictionary')
        except AssertionError as _e:
            print(_e)
    #todo: output error in vim

    @classmethod
    def _esm_element_is_normal(cls, dictionary, name):
        #todo: use regex to find the repo name
        return False

    @classmethod
    def _esm_element_is_bsp(cls, dictionary, name):
        #todo: use regex to find the repo name
        return False

    @classmethod
    def _esm_element_is_port(cls, dictionary, name):
        #todo: use regex to find the repo name
        return False

    @classmethod
    def _esm_element_is_group(cls, dictionary):
        if cls._dict_depth(dictionary) > 1:
            return True
        return False

    @classmethod
    def _dict_depth(cls, dictionary):
        if isinstance(dictionary, dict):
            return 1 + (max(map(cls._dict_depth, dictionary.values())) if dictionary else 0)
        return 0

    @classmethod
    def _esm_find_key_in_dict(cls, dictionary, keyword):
        cls.key_list.clear()
        cls.element_dict.clear()
        for k, v in dictionary.items():
            if k == keyword:
                cls.key_list.append(k)
                if isinstance(v, dict):
                    cls.element_dict = v.copy()
                return True
            elif isinstance(v, dict):
                if cls._esm_find_key_in_dict(v, keyword):
                    cls.key_list.append(k)
                    return True
        return False


class EsmElementInterface(ABC):

    def __init__(self, key_path, name, element_type):
        self.element_type = element_type
        self.key_path = key_path
        self.name = name


    @abstractstaticmethod
    def get_update_file_command():
        """interface method"""


    def get_update_command(self):
        return self._esm_command('update')


    def get_diff_command(self):
        return self._esm_command('diff')


    def get_clean_command(self):
        return self._esm_command('clean')


    def _esm_command(self, command_option):
        command_str = 'svnext '+ command_option + ' --overwrite-local-changes -e ' + self.key_path
        return command_str


class EsmElementNormal(EsmElementInterface):
    def __init__(self, key_path, name, url, rev):
        super().__init__(key_path, name, 'normal')
        self.url =  url
        self.revison = rev


    def get_update_file_command(self):
        return None


    # def update_revision(self, requested_revison='HEAD')
    #     if requested_revison == 'HEAD':
    #         # get svn head rev from
    #     else:
    #         self.revison = requested_revison


    def get_branch_list(self):
        # extract brach dir from url and return list
        pass


    def get_tag_list(self):
        # extract tags dir from url and return list
        pass


    def set_url_and_update_revision(self, new_url):
        self.url = new_url
        self.update_revision()


class EsmElementPort(EsmElementInterface):

    def __init__(self, key_path, name, url, rev):
        super().__init__(key_path, name, 'port')
        self.url =  url
        self.revison = rev


    def get_update_file_command(self):
        return None

    # def update_revision(self, requested_revison='HEAD')
    #     if requested_revison == 'HEAD':
    #         # get svn head rev from
    #     else:
    #         self.revison = requested_revison


    def get_branch_list(self):
        # extract brach dir from url and return list
        pass


    def get_tag_list(self):
        # extract tags dir from url and return list
        pass


    def set_url_and_update_revision(self, new_url):
        self.url = new_url
        self.update_revision()


class EsmElementGroup(EsmElementInterface):
    def __init__(self, key_path, name):
        super().__init__(key_path, name, 'group')

    def get_update_file_command(self):
        return None

    def _esm_command(self, command_option):
        command_str = 'svnext '+ command_option + ' --overwrite-local-changes -g ' + self.key_path
        return command_str


class EsmElementBsp(EsmElementInterface):
    def __init__(self, key_path, name, url, rev):
        super().__init__(key_path, name, 'bsp')
        self.url =  url
        self.revison = rev

    def get_update_file_command(self):
        return None
