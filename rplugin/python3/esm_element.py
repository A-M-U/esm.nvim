from abc import ABC, abstractstaticmethod
import re
import os
import subprocess

class EsmElementFactory():
    key_list = []
    element_dict = {}

    @classmethod
    def get_element(cls, externals, keyword):
        if cls._esm_find_key_in_dict(externals, keyword):
            key_path = "/".join(cls.key_list[::-1])
            element_name = cls.key_list[0]
            if cls._esm_element_is_group(cls.element_dict):
                return EsmElementGroup(key_path, element_name)
            else:
                element_url = cls.element_dict['url']
                element_rev = cls.element_dict['revision']
                if cls._esm_element_is_bsp(element_url, element_name):
                    return EsmElementBsp(key_path, element_name, element_url, element_rev)
                elif cls._esm_element_is_rpc(element_url, element_name):
                    return EsmElementRpc(key_path, element_name, element_url, element_rev)
                elif cls._esm_element_is_port(element_url, element_name):
                    return EsmElementPort(key_path, element_name, element_url, element_rev)
                else:
                    return EsmElementNormal(key_path, element_name, element_url, element_rev)
        raise AssertionError('keyword: "{}" not found in dictionary'.format(keyword))

    @classmethod
    def _esm_element_is_bsp(cls, element_url, element_name):
        repo_list = ['Repository_BSP']

        for repo in repo_list:
            if re.search(repo, element_url):
                return True
        return False

    @classmethod
    def _esm_element_is_rpc(cls, element_url, element_name):
        repo_list = ['Repository_RadarProcessingChain']

        for repo in repo_list:
            if re.search(repo, element_url):
                return True
        return False

    @classmethod
    def _esm_element_is_port(cls, element_url, element_name):
        repo_list = ['Repository_Ports']

        for repo in repo_list:
            if re.search(repo, element_url):
                return True
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
        return self._esm_command('update', ['--overwrite-local-changes'])


    def get_diff_command(self):
        return self._esm_command('diff')


    def get_clean_command(self):
        return self._esm_command('clean')


    def _esm_command(self, command_option, command_attributes_list=None):
        command_attributes = ''
        if command_attributes_list is not None:
            command_attributes = ' ' + ' '.join(command_attributes_list)

        command_str = 'svnext '+ command_option + command_attributes + ' -e ' + self.key_path
        return command_str


    def update_revision(self):
        result = subprocess.run('svn info --show-item last-changed-revision ' + self.url, stdout=subprocess.PIPE)
        self.revision = result.stdout.strip().decode('utf-8')
        return result.stdout.strip().decode('utf-8')


    def get_url_list(self, branch_type):
        element_repo_root_path = ''
        if re.search(r'/tags/', self.url):
            element_repo_root_path = self.url.split(r'/tags/')[0]
        elif re.search(r'/trunk/', self.url):
            splitted_url = self.url.split(r'/trunk/')
            if len(splitted_url) > 2:
                # in some repo urls the work trunk is available multiple times. Hence it is necessary to build the
                # element_repo_root_path using all values of the splitted_url list except the last list index
                element_repo_root_path = r'/trunk/'.join(splitted_url[:-1])
            else:
                element_repo_root_path = splitted_url[0]
        elif re.search(r'/branches/', self.url):
            element_repo_root_path = self.url.split(r'/branches/')[0]

        result = subprocess.run('svn ls ' + element_repo_root_path + r'/' + branch_type, stdout=subprocess.PIPE)

        return result.stdout.decode('utf-8').strip(os.linesep).split(os.linesep)


class EsmElementNormal(EsmElementInterface):
    def __init__(self, key_path, name, url, rev):
        super().__init__(key_path, name, 'normal')
        self.url =  url
        self.revision = rev


    def get_update_file_command(self):
        raise AssertionError('commmand not supported for esm_element_type: normal')


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
        self.revision = rev


    def get_update_file_command(self):
        raise AssertionError('commmand not supported for esm_element_type: port')


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
        raise AssertionError('commmand not supported for esm_element_type: group')

    def update_revision(self):
        raise AssertionError('commmand not supported for esm_element_type: group')

    def _esm_command(self, command_option, command_attributes_list=None):
        command_attributes = ''
        if command_attributes_list is not None:
            command_attributes = ' ' + ' '.join(command_attributes_list)

        command_str = 'svnext '+ command_option + command_attributes + ' -g ' + self.key_path
        return command_str


class EsmElementBsp(EsmElementInterface):
    def __init__(self, key_path, name, url, rev):
        super().__init__(key_path, name, 'bsp')
        self.url =  url
        self.revision = rev

    def get_update_file_command(self):
        return None


class EsmElementRpc(EsmElementInterface):
    def __init__(self, key_path, name, url, rev):
        super().__init__(key_path, name, 'rpc')
        self.url =  url
        self.revision = rev

    def get_update_file_command(self):
        return None


