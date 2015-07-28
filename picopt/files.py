from __future__ import print_function
import os
import multiprocessing

import comic
import detect_format
import optimize_image
from settings import Settings
import stats
import timestamp


def optimize_file(filename_full, multiproc, optimize_after):
    """ Optimize an individual file """
    if optimize_after is not None:
        mtime = os.stat(filename_full).st_mtime
        if mtime <= optimize_after:
            return

    image_format = detect_format.detect_file(filename_full)
    if not image_format:
        return

    if Settings.list_only:
        # list only
        print("%s : %s" % (filename_full, image_format))
    elif detect_format.is_format_selected(image_format, comic.FORMATS,
                                          comic.PROGRAMS):
        return comic.optimize_comic_archive(filename_full, image_format,
                                            multiproc, optimize_after)
    else:
        # regular image
        args = [filename_full, image_format, Settings,
                multiproc['in'], multiproc['out'], multiproc['nag_about_gifs']]
        return multiproc['pool'].apply_async(optimize_image.optimize_image,
                                             args=(args,))


def optimize_dir(filename_full, multiproc, optimize_after, recurse=None):
    """ Recursively optimize a directory """
    if recurse is None:
        recurse = Settings.recurse

    if not recurse:
        return set()
    next_dir_list = os.listdir(filename_full)
    next_dir_list.sort()
    optimize_after = timestamp.get_optimize_after(filename_full, False,
                                                  optimize_after)
    return optimize_files(filename_full, next_dir_list, multiproc,
                          optimize_after)


def optimize_files(cwd, filter_list, multiproc, optimize_after, recurse=None):
    """sorts through a list of files, decends directories and
       calls the optimizer on the extant files"""
    if recurse is None:
        recurse = Settings.recurse

    result_set = set()
    for filename in filter_list:

        filename_full = os.path.join(cwd, filename)
        filename_full = os.path.normpath(filename_full)

        if not Settings.follow_symlinks and os.path.islink(filename_full):
            continue
        elif os.path.basename(filename_full) == timestamp.RECORD_FILENAME:
            continue
        elif os.path.isdir(filename_full):
            results = optimize_dir(filename_full, multiproc,
                                   optimize_after, recurse)
            result_set = result_set.union(results)
        elif os.path.exists(filename_full):
            result = optimize_file(filename_full, multiproc,
                                   optimize_after)
            if result:
                result_set.add(result)
        elif Settings.verbose:
            print(filename_full, 'was not found.')
    return result_set


def optimize_files_after(path, file_list, multiproc):
    """ compute the optimize after date for the a batch of files
        and then optimize them.
    """
    optimize_after = timestamp.get_optimize_after(path, True, None)
    return optimize_files(path, file_list, multiproc, optimize_after)


def optimize_all_files(multiproc):
    """ Optimize the files from the arugments list in two batches.
        One for absolute paths which are probably outside the current
        working directory tree and one for relative files.
    """
    # Change dirs
    os.chdir(Settings.dir)
    cwd = os.getcwd()

    # Init records
    record_dirs = set()
    cwd_files = set()

    for filename in Settings.paths:
        # Record dirs to put timestamps in later
        if Settings.recurse and os.path.isdir(filename):
            record_dirs.add(filename)

        # Optimize all filenames that are not immediate descendants of
        #   the cwd and compute their optimize-after times individually.
        #   Otherwise add the files to the list to do next
        path_dn, path_fn = os.path.split(os.path.realpath(filename))
        if path_dn != cwd:
            optimize_files_after(path_dn, [path_fn], multiproc)
        else:
            cwd_files.add(path_fn)

    # Optimize immediate descendants with optimize after computed from
    # the current directory
    if len(cwd_files):
        optimize_files_after(cwd, cwd_files, multiproc)

    return record_dirs


def optimize():
    """ use preconfigured settings to optimize files """

    # Setup Multiprocessing
    manager = multiprocessing.Manager()
    total_bytes_in = manager.Value(int, 0)
    total_bytes_out = manager.Value(int, 0)
    nag_about_gifs = manager.Value(bool, False)
    pool = multiprocessing.Pool(Settings.jobs)

    multiproc = {'pool': pool, 'in': total_bytes_in, 'out': total_bytes_out,
                 'nag_about_gifs': nag_about_gifs}

    # Optimize Files
    record_dirs = optimize_all_files(multiproc)

    # Shut down multiprocessing
    pool.close()
    pool.join()

    # Write timestamps
    for filename in record_dirs:
        timestamp.record_timestamp(filename)

    # Finish by reporting totals
    stats.report_totals(multiproc['in'].get(), multiproc['out'].get(),
                        multiproc['nag_about_gifs'].get())
