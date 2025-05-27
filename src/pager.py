import os
from constants import PAGE_SIZE
from storage import Page

# 1. File Backed Storage
# Pager should handle a single file on disk where all pages are stored.

class Pager:
    def __init__(self,file_path, max_cache_size = 100*PAGE_SIZE):
        # we need a file to read
        self.file_path = file_path
        # max amount of pages will be 100
        self.max_cache_size = max_cache_size
        # create a cache storage for page_ids
        self.cache = {}
        # keep track of what pages have content on them to not overwrite
        self.dirty_pages = set()

        # open or create a file to use as storage for pages
        if not os.path.exists(self.file_path): 
                self.file = open(self.file_path,'w+b') 
        else:
                self.file = open(self.file_path,'r+b') 

            
            
    
    # retrieve a page from file
    def get_page(self,page_id):
        # if we have this page_id in cache just return it
        if page_id in self.cache:
              return self.cache[page_id]
        # otherwise we need to identify the positon of the page in the file and return that bytestream as a nice page
        else:
            #  get location offset in pager
            offset = page_id * PAGE_SIZE
            # move to that location
            self.file.seek(offset)
            # extract contents from that location
            raw_data = self.file.read(PAGE_SIZE)
            # bring in a page and deserialize those contents
            page = Page.from_bytes(page_id = page_id, raw = raw_data)
            # store it in cache and return it
            self.cache[page_id] = page
            return page