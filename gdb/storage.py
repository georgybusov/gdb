class Page:
    # - memory counter how much memory does this page hold right now
    # - maximum memory per page (we want 4096 Bytes)
    # - value container (this is where we hold values and we must not exceed 4096 in total value memory)
    # - serialization function (this take values and turns them into bytes)
    # - deserialization function (look at the bytes in the format mentioned above and turn it into readable text)

    def __init__(self, max_size = 4096):
        self.max_size = max_size
        self.current_size = 0
        self.values = []


    def add_value(self, value:bytes):
        # byte_value = bytes(value, 'utf-8') this only need to be here if you you are struggling with trasnforming this later
        value_memory_usage = len(value) + 4 #4 for the prefix and len(byte_value) to get the memory of the value as each string character is 1 byte
        if value_memory_usage + self.current_size > self.max_size:
            raise ValueError("Value too big")
        self.values.append(value)
        self.current_size +=value_memory_usage


    def to_bytes(self):
        # get the length of the value (because you need to prefix you data with its length so that we konw how much to read)
        byte_list = bytearray() #make an empty bytearray like you would a list when appending values
        for val in self.values:
            prefix = len(val)
            byte_list.extend(prefix.to_bytes(4,'big'))
            byte_list.extend(val)
        return bytes(byte_list) #this must be returned as bytes(byte_list) so that its immutable during travel
    
    @staticmethod
    def from_bytes(raw:bytes) -> "Page":
        page = Page() #create a new page to hold the disk values with default max_size
        
        i = 0 #this is the index which is used to traverse the byte stream and identify prefixes and values
        while i < len(raw):
            length = int.from_bytes(raw[i:i+4],'big')
            i+=4 #once you extracted the prefix, you can move the index forward by size of prefix (prefixed* to 4)
            current_encoded_value = raw[i:i+length] #isolate the value for the "raw" byte stream
            page.add_value(current_encoded_value)
            i+=length
        return page