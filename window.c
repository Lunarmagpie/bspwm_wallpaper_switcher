#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdio.h>
#include <dirent.h>
#include <stdlib.h>
#include <string.h>

#include <X11/Xlib.h>
#include <Imlib2.h>

#define FILETYPE ".bmp" 

struct X11Info {
    Display *d;
    Pixmap bitmap;
    Window root;
};

struct X11Info*
get_info(int pixmapWidth, int pixmapHeight)
{
    struct X11Info info;
    info.d = XOpenDisplay(NULL);
    info.root = RootWindow(info.d, DefaultScreen(info.d));
    info.bitmap = XCreatePixmap(info.d, info.root, pixmapWidth, pixmapHeight, DefaultDepth(info.d, 0));

    return 0;
}

void set_window(struct X11Info info, Imlib_Image img, int x, int y)
{
    Display *d = info.d;
    Pixmap bitmap = info.bitmap;
    Window root = info.root;

    int s = DefaultScreen(d);

    imlib_context_set_image(img);

    int width = imlib_image_get_width();
    int height = imlib_image_get_height();

    imlib_context_set_display(d);
    imlib_context_set_visual(DefaultVisual(d, 0));
    imlib_context_set_colormap(DefaultColormap(d, 0));
    imlib_context_set_drawable(bitmap);

    imlib_render_image_on_drawable(x, y);

    // Set the properties
    // <https://github.com/l3ib/nitrogen/blob/master/src/SetBG.cc>

    Atom prop_root, prop_esetroot, type;

    prop_root = XInternAtom(d, "_XROOTPMAP_ID", False);
    prop_esetroot = XInternAtom(d, "ESETROOT_PMAP_ID", False);

    if (prop_root == None || prop_esetroot == None) {
        // printf _("ERROR: BG set could not make atoms.") << "\n";
        return;
    }

    Atom XA_PIXMAP = 20;
    XChangeProperty(d, root, prop_root, XA_PIXMAP, 32, PropModeReplace, (unsigned char *) &(bitmap), 1);
    XChangeProperty(d, root, prop_esetroot, XA_PIXMAP, 32, PropModeReplace, (unsigned char *) &(bitmap), 1);

    XSetWindowBackgroundPixmap(d, root, bitmap);
    XFlush(d);
    XClearWindow(d, root);
}

static PyMethodDef Methods[] = {
    {"get_info",  get_info, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "backgrounds",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    Methods
};


PyMODINIT_FUNC
PyInit_spam(void)
{
    PyObject *m;

    m = PyModule_Create(&module);
    if (m == NULL)
        return NULL;

    return m;
}