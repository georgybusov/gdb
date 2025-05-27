



# 1. File Backed Storage
# Pager should handle a single file on disk where all pages are stored.

class Pager:
    def __init__(self,file_path, max_cache_size = 100*4096):
        # we need a file to read
        self.file_path = file_path
        # max amount of pages will be 100
        self.max_cache_size = max_cache_size
        # keep track of what pages have content on them to not overwrite
        self.dirty_pages = set()