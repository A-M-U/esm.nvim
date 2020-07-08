

class EsmElement():


    def __init__(self, key_path, name, url, rev):
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



