import os
import multiprocessing

import extern


class Settings(object):
    """ a global settings class """
    advpng = False
    archive_name = None
    bigger = False
    comics = False
    destroy_metadata = False
    dir = os.getcwd()
    follow_symlinks = True
    formats = set()
    gifsicle = True
    jobs = multiprocessing.cpu_count()
    jpegrescan = True
    jpegrescan_mutithread = False
    jpegtran = True
    jpegtran_prog = True
    list_only = False
    mozjpeg = True
    optimize_after = None
    optipng = True
    paths = set()
    pngout = True
    record_timestamp = False
    recurse = False
    test = False
    to_png_formats = set()
    verbose = 1

    @classmethod
    def update(cls, settings):
        for k, v in settings.__dict__.iteritems():
            if k.startswith('_'):
                continue
            setattr(cls, k, v)

    @classmethod
    def config_program_reqs(cls, programs):
        """run the external program tester on the required binaries"""
        for program in programs:
            val = getattr(cls, program.__name__) \
                and extern.does_external_program_run(program.__name__)
            setattr(cls, program.__name__, val)

        do_png = cls.optipng or cls.pngout or cls.advpng
        do_jpeg = cls.mozjpeg or cls.jpegrescan or cls.jpegtran

        do_comics = cls.comics

        if not do_png and not do_jpeg and not do_comics:
            print("All optimizers are not available or disabled.")
            exit(1)