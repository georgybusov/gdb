class Page:
    def __init__(self,max_size=4096):
        self.max_size = max_size
        self.current_size = 0
        self.values = []

    
    def add_value(self, value:bytes):
        value_size = len(value)
        if self.current_size + value_size > self.max_size:
            raise ValueError("not enough space in page to store value")
        self.values.append(value)
        self.current_size+=value_size



    def to_bytes(self):
        """
        Serialization: Combine all values into a single byte stream prefixed with each value's length
        """
        result = bytearray() # create an empty byte array similar to how you do empty lists when appending results from a for loop
        for val in self.values: 
            length=len(val) # need to prefix each byte with length so that we know how much of the following byte to read
            result.extend(length.to_bytes(4,byteorder='big')) # generating prefix for each value and appending it to the result
            result.extend(val) # appending each value to result
        return bytes(result)
    
    def from_bytes(raw: bytes, max_size=4096):
        """
        Deserialize raw bytes into a Page object, parsing values by reading
        each length-prefixed value in sequence.
        """
        page = Page(max_size=max_size)  # create an instance of a page
        i = 0  # keep track of position in array
        
        while i < len(raw):
            length = int.from_bytes(raw[i:i+4], byteorder='big')  # read the length of the next value (this is 4 bytes because we prefixed every value with a 4 byte hexadecimal integer)
            i += 4  # Move index forward by 4 bytes (this is the length of the length field and this puts us at start of the value)
            
            val = raw[i:i+length]  # extract the value using the length from the line 38
            
            page.add_value(val)  # Add the value to the page
            
            i += length  # move index forward by the length of the value you jsut added so that we are now on the length field of the next value
            
        return page
    


