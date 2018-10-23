#
# restore.py
# ==========
#
# Given an .ini and a .zip file, iterate over all entries in the .ini and 
# move the corresponding files to the specified final location.
#
# Entry Format:
#   [restore]
#   <path on the zip archive>=<path to be placed on new machine>
#
# Example Entries (one toplevel file, one nested file, one directory)
#    [restore]
#    test_reqs.txt = test_reqs.txt
#    ws_test/funkybomb_test.py = ws_test/funkybomb_test.py
#    test_dir/ = test_dir_restored
#
#  ** Make sure to put a trailing slash in the option name if it is a directory! **
#
#
import argparse
import configparser
import os
import shutil
import tempfile
import zipfile

# tempfile.TemporaryDirectory() is only a python3.2+ function, so need to check
# what we're running as.  Determines whether we use a closure or have to
# manually delete temporary directories.
if hasattr(tempfile, "TemporaryDirectory"):
    USE_CLOSURE = True
else:
    USE_CLOSURE = False
    
def _perform_extraction(conf, zf, stagepath):
    """ 
    Given a zip file and a configuration, iterate over all the sections
    of the configuration and use the options and option values to determine
    1. What files to extract from the zip
    2. Where to move the extracted files
    
    @param conf         : ConfigParser object
    @param zf           : zipfile object
    @param stagepath    : directory path for extracted file staging
    """
    zf_namelist = zf.namelist()
    for src, dst in [(opt, conf.get(sec, opt)) for sec in conf.sections() for opt in conf.options(sec)]:
        targets = [z for z in zf_namelist if z.startswith(src)]
        if len(targets) > 1:
            for zf_entry in targets:
                #print("Extracting {} ...".format(zf_entry))
                zf.extract(zf_entry, path=stagepath)
                #print("  - Config Source: {}".format(src))
                #print("  - Destination Path: {}".format(dst))
                #print("  - Zipfile path: {}".format(zf_entry))
                #print("  - Zipfile path adjusted: {}".format(zf_entry.replace(src, "", 1)))
                #print("  -> {}\n  -> {}".format(os.path.join(stagepath, zf_entry), os.path.join(dst, zf_entry.replace(src, "", 1))))
                shutil.move(os.path.join(stagepath, zf_entry), os.path.join(dst, zf_entry.replace(src+"/", "", 1)))
        else:
            zf_entry = src
            zf.extract(zf_entry, path=stagepath)
            shutil.move(os.path.join(stagepath, zf_entry), dst)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="restore.py")
    parser.add_argument("ifile", help="Path to .ini file")
    parser.add_argument("zfile", help="Path to .zip file")
    
    args = parser.parse_args()
    
    cp = configparser.ConfigParser()
    cp.read(args.ifile)
    
    zf = zipfile.ZipFile(args.zfile)
    #print("{}".format(zf.namelist()))
    
    if USE_CLOSURE:
        with tempfile.TemporaryDirectory() as tmpdirname:
            _perform_extraction(cp, zf, tmpdirname)
    else:
        tmpdirname = tempfile.mkdtemp()
        _perform_extraction(cp, zf, tmpdirname)
        print("Removing {}".format(tmpdirname))
        shutil.rmtree(tmpdirname) # os.rmdir() does not remove non-empty directories...
    
