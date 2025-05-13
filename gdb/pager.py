import os
from .storage import Page

class Pager:
    def __init__(self, file_path:str):
        # Does the file exist? Create with writing priviliges if not, or reading priviliges if yes
        if not os.path.exists(file_path): 
                self.file = open(file_path,'w+b') 
        else:
                self.file = open(file_path,'r+b') 
        self.page_size = 4096
        self.cache = {}
        

    def get_page(self, page_id):
        if page_id in self.cache: # if already in cache, return the page
                return self.cache[page_id]
        else: # if not read the page from disc
                offset = self.page_size * page_id #since we are storing pages in order, the id of a page denotes its position in memory
                self.file.seek(offset) # move to the location where the page starts
                raw_data = self.file.read(self.page_size)
                page = Page.from_bytes(raw_data) # create a page from the memory you just read in
                self.cache[page_id]=page # store the page in the cache
                return page
                
    def flush_page(self,page_id):
        if page_id not in self.cache: #if page already not in cache then exit the function
                return
        page = self.cache[page_id] # retrieve the in-memory page to persist it
        serialized_data = page.to_bytes() #serialize the page and return it as a new variable in bytes format
        offset = self.page_size * page_id #find the correct location to store this page
        self.file.seek(offset) # move to the location on disc where the page needs to start
        self.file.write(serialized_data) #  write the raw data to this location of the file
        self.file.flush() # flush internal write buffer immediately


    def flush_all(self):
        for page_id, page in self.cache.items():
                serialized_data = page.to_bytes() #serialize the page and return it as a new variable in bytes format
                offset = self.page_size * page_id #find the correct location to store this page
                self.file.seek(offset) # move to the location on disc where the page needs to start
                self.file.write(serialized_data) #  write the raw data to this location of the file
        self.file.flush() # flush internal write buffer immediately after loop ends

    def num_pages(self): #how many pages are in this Pager
        file_size = os.path.getsize(self.file.name)
        page_count = file_size // self.page_size
        return page_count