Guitar Pro files version and metadata detect
======================

Usage::

    f = open(fullpath, 'rb')
    gp = GuitarProFileSimple(f)
    print gp.version, gp.artist, gp.title
