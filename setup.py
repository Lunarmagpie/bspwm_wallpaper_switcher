from distutils.core import setup, Extension

module1 = Extension('backgrounds',
                    sources=['window.c'],
                    libraries=["X11", "Imlib2"],
)

setup(name='PackageName',
      version='1.0',
      description='This is a demo package',
      ext_modules=[module1])
