from distutils.core import setup, Extension

module1 = Extension('backgrounds',
                    sources=['window.c'],
                    libraries=["lX11", "lImlib2"],
                    library_dirs=[
                        "/usr/lib/gcc/x86_64-pc-linux-gnu/12.1.0/include",
                        "/usr/local/include",
                        "/usr/lib/gcc/x86_64-pc-linux-gnu/12.1.0/include-fixed",
                        "/usr/include",
                    ],
                    include_dirs=[
                        "/usr/lib/gcc/x86_64-pc-linux-gnu/12.1.0/include",
                        "/usr/local/include",
                        "/usr/lib/gcc/x86_64-pc-linux-gnu/12.1.0/include-fixed",
                        "/usr/include",
                    ])

setup(name='PackageName',
      version='1.0',
      description='This is a demo package',
      ext_modules=[module1])
