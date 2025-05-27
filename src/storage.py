class Page:
    def __init__(self, page_id: int, max_size: int = 4096, data: bytes = None):
        #page instance is for storing values 
        self.values = [] 
        #all page instances need to be identically sized
        self.max_size = max_size 
        # identify a given page instance
        self.page_id = page_id 
        #keeping track of capacity of the page instnace
        self.current_size = 0 
        # keep track of deleted slots (disabling fragmentation)
        self.deleted_indices = set() 

        # Give it option to pass data into fresh instance
        if data:
            self._load_from_bytes(data)


    def add_value(self, value: bytes) -> int:
        #track how much memory will we need to add value to a page
        value_memory_usage = len(value) + 4 
        if self.current_size + value_memory_usage > self.max_size:
            raise ValueError("Value too big for page.") 
        
        #if there are deleted indices lets reuse last deleted page_id
        if self.deleted_indices: 
            row_id = self.deleted_indices.pop()
            #write into the row_id you identified
            self.values[row_id] = value 
            # occupy this capacity
            self.current_size += value_memory_usage
        else:
            # otherwise append it to the values list
            self.values.append(value)
            self.current_size += value_memory_usage
            # assign row_id with value position
            row_id = len(self.values) - 1 

        return row_id

    #get value from the page given it's row id
    def get_value(self, row_id: int) -> bytes:
        #Check if this row id is even available (not deleted, not out of index)
        if row_id >= 0 and row_id < len(self.values) and row_id not in self.deleted_indices:
            return self.values[row_id]
        else:
            raise IndexError(f"Row id {row_id} not on {self.page_id} or deleted")

    #delete a value at a given row id (keep the row but make value contents null)
    def delete_value(self, row_id: int):
        #Check if this row id is even available (not deleted, not out of index)
        if row_id >= 0 and row_id < len(self.values) and row_id not in self.deleted_indices:
            #record how much space will be freed up upon deletion
            deleted_value_size = len(self.values[row_id]) + 4 
            # nullify the value at row_id's location
            self.values[row_id] = None 
            # now decrement
            self.current_size -= deleted_value_size 
            #record that you deleted it
            self.deleted_indices.add(row_id) 
        else:
            raise IndexError(f"Row id {row_id} not on {self.page_id} or deleted")


    # Serialize a given page into a bytestream that can be pushed to memory
    def to_bytes(self) -> bytes:
        # initialize a byte stream which we will fill with the page's values after serialization
        byte_list = bytearray()
        # Loop through values and turn transform them to bytes with prefixes that specify their lengths
        for i, value in enumerate(self.values):
            # 0-length prefixes awarded to deleted rows (trade off decision, alternatives too complicated)
            if i in self.deleted_indices:
                #send 0 to byte stream if values are null    
                byte_list.extend((0).to_bytes(4, 'big')) 
            else:
                #record how many values are coming
                prefix = len(value) 
                #send this prefix and values to bytestream
                byte_list.extend(prefix.to_bytes(4, 'big'))
                byte_list.extend(value)

        # Create padding for pages that aren't full based on how much space is left out of max_size
        padding = self.max_size - len(byte_list)
        #Check if bytestream is more than a page in gdb (over 4KB)
        if padding < 0: 
            raise ValueError("Too much content for gdb's page size")
        #fill whatever space is left in the bytestream up to 4KB with padding
        byte_list.extend(b'\x00' * padding) 
        return bytes(byte_list)

    # Load a page instance from a given bytestream
    def _load_from_bytes(self, raw: bytes):
        # start an index that shows us where in the bytestream we are and set reading cutoff limit
        i = 0
        # loop contents of the bytestream (minimum 4 --> if next value = deleted row prefix)
        while i + 4 <= len(raw):
            #read prefix and assign it to length and move past it
            length_bytes = raw[i:i+4]
            length = int.from_bytes(length_bytes, 'big') 
            i += 4

            #if value == 0 then this is a deleted row (previous tradeoff decision)
            if length == 0:
                #mark row as null and add it to deleted_indices
                self.values.append(None)
                self.deleted_indices.add(len(self.values) - 1)
                continue
            # check if prefix+value is longer than bytestream (shouldn't be possible)
            if i + length > len(raw):
                break  # Incomplete value — stop loading
            
            # identify value
            value = raw[i:i+length]
            # append value to page's values
            self.values.append(value)
            #increment size of page
            self.current_size += length + 4
            # move index
            i += length

        # Recalculate page capacity to exclude deleted slots or padding
        self.current_size = 0
        # Loop over values you just appended from the bytestream to the page instance
        for i, value in enumerate(self.values):
            # Increment to current_size for every valid value entry
            if value is not None and i not in self.deleted_indices:
                self.current_size += len(value) + 4

    # Create a page from raw bytes leveraging the init and _load_from_bytes methods
    @staticmethod
    def from_bytes(page_id: int, raw: bytes, max_size: int = 4096) -> "Page":
        page = Page(page_id=page_id, max_size=max_size, data=raw)
        return page