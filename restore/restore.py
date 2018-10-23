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
#    ws_test/funkybomb_test.py = ws_test_restored/funkybomb_test.py
#    test_dir = test_dir_restored
#
import argparse
try:
    import configparser
except:
    import ConfigParser as configparser
import os
import shutil
import tempfile
import zipfile


def _perform_extraction(conf, zf, stagepath):
    """
    Given a zip file and a configuration, iterate over all the sections
    of the configuration and use the opstions and option values to determine
    1. What files to extract from the zip
    2. Where to move the extracted files

    @param conf         : ConfigParser object
    @param zf           : zipfile.ZipFile object
    @param stagepath    : directory path for extracted file staging
    """
    zf_namelist = zf.namelist()
    for src, dst in [(opt, conf.get(sec, opt)) for sec in conf.sections() for opt in conf.options(sec)]:
    
        srcdir = os.path.dirname(src)
        srcname = os.path.basename(src)
        
        dstdir = os.path.dirname(dst)
        dstname = os.path.basename(dst)

        for zf_name in [z for z in zf_namelist if z.startswith(src) and not z.endswith("/")]:
            #print("zipfile entry: {}".format(zf_name))
            zdir = os.path.dirname(zf_name)
            zname = os.path.basename(zf_name)

            extractpath = os.path.join(stagepath, zf_name)

            # Extract to staging directory
            print("Extracting to {}".format(extractpath))
            zf.extract(zf_name, path=stagepath)

            # Create final directory/directories  
            movepath = os.path.join(zf_name.replace(src, dst, 1))
            movedir = os.path.dirname(movepath)
            if len(movedir) > 0 and not os.path.isdir(movedir):
                #print("Making folders: {}".format(os.path.dirname(movepath)))
                os.makedirs(movedir)

            # Move to final directory
            print(" - Moving: {} -> {}".format(extractpath, movepath))
            shutil.move(extractpath, movepath)
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Restore files and folders.")
    parser.add_argument("ifile", help="Path to .ini file")
    parser.add_argument("zfile", help="Path to .zip file")
    
    args = parser.parse_args()
    
    cp = configparser.ConfigParser()
    cp.optionxform = str    # This is needed so that ConfigParser keeps case of the sections!!
    cp.read(args.ifile)
    
    zf = zipfile.ZipFile(args.zfile)
    #print("{}".format(zf.namelist()))
    
    tmpdir = tempfile.mkdtemp()
    _perform_extraction(cp, zf, tmpdir)
    shutil.rmtree(tmpdir)   # os.rmdir() does not remove non-empty directories...
            
