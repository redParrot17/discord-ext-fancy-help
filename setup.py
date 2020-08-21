from setuptools import setup
import re

with open('discord/ext/fancyhelp/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

if version.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass

setup(name='discord-ext-fancy-help',
      author='redParrot17',
      url='https://github.com/redParrot17/discord-ext-fancy-help',
      version=version,
      packages=['discord.ext.fancyhelp'],
      license='MIT',
      description='An extension module to make embed based help menus with discord.py',
      install_requires=['discord.py>=1.2.5'],
      python_requires='>=3.6.0'
)
