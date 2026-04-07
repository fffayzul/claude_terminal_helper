/*
 * scanner.c — Fast recursive file scanner implemented as a Python C extension.
 *
 * Exposes one function to Python:
 *   scan(path: str, min_bytes: int = 0) -> list[dict]
 *
 * Each dict has keys: path (str), size (int), extension (str).
 *
 * Build with:
 *   cd scanner && python setup.py build_ext --inplace
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <sys/stat.h>
#include <dirent.h>
#include <string.h>
#include <stdlib.h>

/* Append one file-info dict to a Python list. */
static int append_file(PyObject *list, const char *full_path, off_t size) {
    const char *dot = strrchr(full_path, '.');
    const char *ext = dot ? dot : "";

    PyObject *d = PyDict_New();
    if (!d) return -1;

    PyDict_SetItemString(d, "path",      PyUnicode_FromString(full_path));
    PyDict_SetItemString(d, "size",      PyLong_FromLong((long)size));
    PyDict_SetItemString(d, "extension", PyUnicode_FromString(ext));

    int rc = PyList_Append(list, d);
    Py_DECREF(d);
    return rc;
}

/* Recursive walk. */
static int walk(const char *base, long min_bytes, PyObject *list) {
    DIR *dir = opendir(base);
    if (!dir) return 0;

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;  /* skip hidden / . / .. */

        /* Build full path */
        size_t base_len = strlen(base);
        size_t name_len = strlen(entry->d_name);
        char *full = malloc(base_len + name_len + 2);
        if (!full) { closedir(dir); return -1; }
        memcpy(full, base, base_len);
        full[base_len] = '/';
        memcpy(full + base_len + 1, entry->d_name, name_len + 1);

        struct stat st;
        if (stat(full, &st) == 0) {
            if (S_ISDIR(st.st_mode)) {
                walk(full, min_bytes, list);
            } else if (S_ISREG(st.st_mode) && st.st_size >= min_bytes) {
                append_file(list, full, st.st_size);
            }
        }
        free(full);
    }
    closedir(dir);
    return 0;
}

/* Python-callable: scan(path, min_bytes=0) */
static PyObject *py_scan(PyObject *self, PyObject *args, PyObject *kwargs) {
    const char *path;
    long min_bytes = 0;
    static char *kwlist[] = {"path", "min_bytes", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s|l", kwlist, &path, &min_bytes))
        return NULL;

    PyObject *results = PyList_New(0);
    if (!results) return NULL;

    walk(path, min_bytes, results);
    return results;
}

static PyMethodDef ScannerMethods[] = {
    {"scan", (PyCFunction)py_scan, METH_VARARGS | METH_KEYWORDS,
     "scan(path, min_bytes=0) -> list[dict]\n\n"
     "Recursively scan a directory. Returns list of {path, size, extension}."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef scannermodule = {
    PyModuleDef_HEAD_INIT, "scanner", NULL, -1, ScannerMethods
};

PyMODINIT_FUNC PyInit_scanner(void) {
    return PyModule_Create(&scannermodule);
}
