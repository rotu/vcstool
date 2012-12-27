import os
from xml.etree.ElementTree import fromstring

from .vcs_base import find_executable, VcsClientBase


class SvnClient(VcsClientBase):

    type = 'svn'
    _executable = None

    @staticmethod
    def is_repository(path):
        return os.path.isdir(os.path.join(path, '.svn'))

    def __init__(self, path):
        super(SvnClient, self).__init__(path)

    def branch(self, _command):
        cmd_info = [SvnClient._executable, 'info', '--xml']
        result_info = self._run_command(cmd_info)
        if result_info['returncode']:
            result_info['output'] = 'Could not determine url: %s' % result_info['output']
            return result_info
        info = result_info['output']

        try:
            root = fromstring(info)
            entry = root.find('entry')
            url = entry.findtext('url')
            repository = entry.find('repository')
            root_url = repository.findtext('root')
        except Exception as e:
            return {
                'cmd': '',
                'cwd': self.path,
                'output': "Could not determine url from xml: %s" % e,
                'returncode': 1
            }

        if not url.startswith(root_url):
            return {
                'cmd': '',
                'cwd': self.path,
                'output': "Could not determine url suffix. The root url '%s' is not a prefix of the url '%s'" % (root_url, url),
                'returncode': 1
            }

        return {
            'cmd': ' '.join(cmd_info),
            'cwd': self.path,
            'output': url[len(root_url):],
            'returncode': 0,
        }

    def diff(self, command):
        cmd = [SvnClient._executable, 'diff']
        if command.context:
            cmd += ['--unified=%d' % command.context]
        return self._run_command(cmd)

    def log(self, command):
        cmd = [SvnClient._executable, 'log', '--limit', '%d' % command.limit]
        return self._run_command(cmd)

    def pull(self, _command):
        cmd = [SvnClient._executable, '--non-interactive', 'update']
        return cmd

    def remotes(self, _command):
        cmd_info = [SvnClient._executable, 'info', '--xml']
        result_info = self._run_command(cmd_info)
        if result_info['returncode']:
            result_info['output'] = 'Could not determine url: %s' % result_info['output']
            return result_info
        info = result_info['output']

        try:
            root = fromstring(info)
            entry = root.find('entry')
            url = entry.findtext('url')
        except Exception as e:
            return {
                'cmd': '',
                'cwd': self.path,
                'output': "Could not determine url from xml: %s" % e,
                'returncode': 1
            }

        return {
            'cmd': ' '.join(cmd_info),
            'cwd': self.path,
            'output': url,
            'returncode': 0,
        }

    def status(self, command):
        cmd = [SvnClient._executable, 'status']
        if command.quiet:
            cmd += ['--quiet']
        return self._run_command(cmd)


if not SvnClient._executable:
    SvnClient._executable = find_executable('svn')
