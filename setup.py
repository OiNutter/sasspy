from distutils.core import setup

setup(name='SassPy',
	  version='0.0.1',
	  url='https://github.com/OiNutter/sasspy',
	  download_url='https://github.com/OiNutter/sasspy/tarball/master',
	  description='Python implementation of the Sass and Scss syntaxes',
	  author='Will McKenzie',
	  author_email='will@oinutter.co.uk',
	  packages=['sasspy'],
	  package_dir={'sasspy': 'sasspy'},
	  requires=['regex'],
	  license='MIT License',
	  classifiers=[
	  		'Development Status :: 3 - Alpha',
	  		'Environment :: Web Environment',
	  		'Intended Audience :: Developers',
	  		'License :: OSI Approved :: MIT License',
	  		'Programming Language :: Python :: 2',
        	'Programming Language :: Python :: 2.6',
        	'Programming Language :: Python :: 2.7',
        	'Programming Language :: CSS'
	  ]
)
