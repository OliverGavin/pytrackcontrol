from setuptools import setup

setup(name='pytrackcontrol',
      version='0.1',
      description='A Python library for interpreting face and hand tracking and gestures from pytrackvision to control a system (HCI).',
      url='http://github.com/OliverGavin/pytrackcontrol',
      author='Oliver Gavin',
      author_email='oliver@gavin.ie',
      license='MIT',
      packages=['pytrackcontrol'],
      install_requires=[
          # 'markdown',
      ],
      # dependency_links=['http://github.com/user/repo/tarball/master#egg=package-1.0'],
      test_suite='nose2.collector.collector',
      tests_require=['nose2'],
      zip_safe=False)
