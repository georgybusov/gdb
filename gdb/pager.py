class Pager:
    def __init__(self, file_path, cache_size = 4096*256): # needs to be 1 GB of cache used here
        # Open the database file (or create it)
        if os.path.exists(file_path):
            self.file = open(file_path, 'r+b') # does the file exist? read it
        else:
            self.file = open(file_path, 'w+b') # does the file not exist? create it

        self.cache = {} # initialize the cache and set the max size
        self.cache_size = cache_size
        
        self.page_size = 4096

    def __del__(self):
        if self.file:
            self.file.close()


    def read_from_disk(self,page_id):
        page_offset = page_id * self.page_size

        with open(self.db_file,'rb') as file:
            file.seek(page_offset)

            raw_data = file.read(self.page_size)

            page = Page.from_bytes(raw_data)

        return page


    def get_page(self, page_id):
        if page_id in self.cache:
            return self.cache(page_id)
        else:
            page = read_from_disk(page_id)
            self.cache[page_id]=(page)
            return page