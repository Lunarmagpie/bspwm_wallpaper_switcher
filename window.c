#include <stdio.h>
#include <dirent.h>
#include <stdlib.h>
#include <string.h>

#include <X11/Xlib.h>
#include <Imlib2.h>

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
        if (strcmp(end, ".bmp") == 0)
        {
            char *n = strtok(name, ".bmp");
            int number = atoi(n);

            char fullname[80];
            sprintf(fullname, "%s%s.bmp", dir, name);

            arr[number] = imlib_load_image(fullname);
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
    XSetWindowBackgroundPixmap(d, root, bitmap);
    XClearWindow(d, root);
    XFlush(d);
}
