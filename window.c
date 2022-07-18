#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdio.h>
#include <dirent.h>
#include <stdlib.h>
#include <string.h>

#include <X11/Xlib.h>
#include <Imlib2.h>

#define PY_SSIZE_T_CLEAN

typedef struct {
    PyObject_HEAD;
    Imlib_Image img;
} ImlibImage;

static int
ImlibImage_init(ImlibImage *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {"filepath", NULL};
    PyObject *filepath = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist,
                                     &filepath))
        return -1;

    self->img = imlib_load_image(PyUnicode_DATA(filepath)); 

    return 0;
}

static PyTypeObject ImlibImageType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_init = (initproc) ImlibImage_init,
    .tp_name = "backgrounds.ImlibImage",
    .tp_doc = PyDoc_STR("Custom objects"),
    .tp_basicsize = sizeof(ImlibImage),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
};



typedef struct {
    PyObject_HEAD;
    Display *d;
    Pixmap bitmap;
    Window root;
} BackgroundSetter;

static int
BackgroundSetter_init(BackgroundSetter *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"width", "height", NULL};
    PyObject *width = NULL, *height = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OO", kwlist,
                                     &width, &height))
        return -1;

    int pixmapWidth = PyLong_AsLong(width);
    int pixmapHeight = PyLong_AsLong(height);

    self->d = XOpenDisplay(NULL);
    self->root = RootWindow(self->d, DefaultScreen(self->d));
    self->bitmap = XCreatePixmap(self->d, self->root, pixmapWidth, pixmapHeight, DefaultDepth(self->d, 0));

    return 0;
}

static PyObject*
BackgroundSetter_set_wallpaper(BackgroundSetter *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"img", "x", "y", NULL};
    PyObject *PY_img = NULL, *PY_x = NULL, *PY_y = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O!OO", kwlist,
                                     &ImlibImageType, &PY_img, &PY_x, &PY_y))
    {
        PyErr_SetString(PyExc_TypeError, "Died here");
        return NULL;
    }

    // Imlib_Image img = ((ImlibImage*)PY_img)->img;

    Imlib_Image img = imlib_load_image("/tmp/bspwm_wallpaper/1.bmp");
 
    int x = PyLong_AsLong(PY_x);
    int y = PyLong_AsLong(PY_y);

    imlib_context_set_image(img);

    imlib_context_set_display(self->d);
    imlib_context_set_visual(DefaultVisual(self->d, 0));
    imlib_context_set_colormap(DefaultColormap(self->d, 0));
    imlib_context_set_drawable(self->bitmap);

    imlib_render_image_on_drawable(x, y);

    // Set the properties
    // <https://github.com/l3ib/nitrogen/blob/master/src/SetBG.cc>

    Atom prop_root, prop_esetroot;

    prop_root = XInternAtom(self->d, "_XROOTPMAP_ID", False);
    prop_esetroot = XInternAtom(self->d, "ESETROOT_PMAP_ID", False);

    if (prop_root == None || prop_esetroot == None) {
        // printf _("ERROR: BG set could not make atoms.") << "\n";
        return NULL;
    }

    Atom XA_PIXMAP = 20;
    XChangeProperty(self->d, self->root, prop_root, XA_PIXMAP, 32, PropModeReplace, (unsigned char *) &(self->bitmap), 1);
    XChangeProperty(self->d, self->root, prop_esetroot, XA_PIXMAP, 32, PropModeReplace, (unsigned char *) &(self->bitmap), 1);

    XSetWindowBackgroundPixmap(self->d, self->root, self->bitmap);
    XFlush(self->d);
    XClearWindow(self->d, self->root);

    Py_RETURN_NONE;
}

static PyMethodDef BackgroundSetter_methods[] = {
    {"set_wallpaper", (PyCFunction) BackgroundSetter_set_wallpaper, METH_VARARGS | METH_KEYWORDS,
     "Set the wallpaper"
    },
    {NULL}  /* Sentinel */
};
static PyTypeObject BackgroundType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_init = (initproc) BackgroundSetter_init,
    .tp_name = "backgrounds.BackgroundSetter",
    .tp_doc = PyDoc_STR("Custom objects"),
    .tp_basicsize = sizeof(BackgroundSetter),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_methods =BackgroundSetter_methods,
};


static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "backgrounds",   /* name of module */
    .m_doc = NULL,
    .m_size = -1,
};


PyMODINIT_FUNC
PyInit_backgrounds(void)
{
    PyObject *m;
    if (PyType_Ready(&BackgroundType) < 0)
        return NULL;
    if (PyType_Ready(&ImlibImageType) < 0)
        return NULL;

    m = PyModule_Create(&module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&BackgroundType);
    if (PyModule_AddObject(m, "BackgroundSetter", (PyObject *) &BackgroundType) < 0) {
        Py_DECREF(&BackgroundType);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&ImlibImageType);
    if (PyModule_AddObject(m, "ImlibImage", (PyObject *) &ImlibImageType) < 0) {
        Py_DECREF(&ImlibImageType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}