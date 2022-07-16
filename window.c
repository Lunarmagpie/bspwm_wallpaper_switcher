#include <stdio.h>
#include <dirent.h>
#include <stdlib.h>
#include <string.h>

#include <X11/Xlib.h>
#include <Imlib2.h>

#define FILETYPE ".bmp" 

Display *d;
Window root;
Pixmap bitmap;

int main(int arc, char *argv[])
{
    d = XOpenDisplay(NULL);
    root = RootWindow(d, DefaultScreen(d));

    {
        char *line = NULL;
        size_t len = 0;
        ssize_t lineSize = 0;


        lineSize = getline(&line, &len, stdin);
        int pixmapWidth = atoi(line);
        lineSize = getline(&line, &len, stdin);
        int pixmapHeight = atoi(line);

        bitmap = XCreatePixmap(d, root, pixmapWidth, pixmapHeight, DefaultDepth(d, 0));

        free(line);
    }

    char *directory = argv[1];
    Imlib_Image images[12];
    load_images(directory, images);
    while (1)
    {
        char *line = NULL;
        size_t len = 0;
        ssize_t lineSize = 0;

        lineSize = getline(&line, &len, stdin);
        int img_n = atoi(line);
        lineSize = getline(&line, &len, stdin);
        int x = atoi(line);
        lineSize = getline(&line, &len, stdin);
        int y = atoi(line);

        free(line);
        run(images, img_n, x, y);
    }
    return 0;
}

void load_images(char dir[], Imlib_Image arr[])
{
    struct dirent *de;
    DIR *dr = opendir(dir);
    if (dr == NULL)
    {
        printf("Could not open current directory");
        return;
    }
    while ((de = readdir(dr)) != NULL)
    {
        char *name = de->d_name;
        char *end = strrchr(name, '.');
        if (strcmp(end, FILETYPE) == 0)
        {
            char *n = strtok(name, FILETYPE);
            int number = atoi(n);

            char *fullname = malloc(strlen(dir) * 8 + strlen(name) * 8 + sizeof(FILETYPE));
            sprintf(fullname, "%s%s%s", dir, name, FILETYPE);

            arr[number] = imlib_load_image(fullname);

            free(fullname);
        }
    }
    closedir(dr);
}

void run(Imlib_Image imgs[], int img_n, int x, int y)
{
    int s = DefaultScreen(d);

    Imlib_Image img;
    int width, height;
    img = imgs[img_n];

    imlib_context_set_image(img);

    width = imlib_image_get_width();
    height = imlib_image_get_height();

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
