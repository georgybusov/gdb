class Table:

    def __init__(self,schema):
        self.schema = schema
        
    
    def insert_row(self, row: dict) ->bytearray:
        if set(row.keys()) != set(self.schema.keys()): #checking if row has the correct number of columns and the correct column names
            raise ValueError(f"Columns {list(row.keys())} do not match schema columns {list(self.schema.keys())}")
        
        for column_name, column_info in self.schema.items():
            value = row[column_name] #extract value of the row
            expected_type = column_info["type"] #extract type of the value in this row
            if not isinstance(value, expected_type):
                raise TypeError(f"Column '{column_name}' expects type {expected_type} but got {type(value)}")
    
        row_as_bytes = bytearray()  # encode/serialize the row into bytes
        for column_name,column_type_size in self.schema.items():
            value_from_row = row[column_name] #set a local variable for this for loop as the value you are working with
            value_type = column_type_size['type'] #and the other local variable as the type of this value which you need to check for
            if value_type == int: 
                value_as_bytes = value_from_row.to_bytes(4,'big') #ints will be converted into 4 byte values
                row_as_bytes.extend(value_as_bytes)
            elif value_type ==str:
                prefix = len(value_from_row)
                value_as_bytes = bytes(value_from_row,'utf-8') #strs will be encoded into utf-8 and prefixed to understand their length (classic)
                row_as_bytes.extend(prefix.to_bytes(4,'big'))
                row_as_bytes.extend(value_as_bytes)
            elif value_type ==bool:
                value_as_bytes = value_from_row.to_bytes(1,'big') #booleans will be single byte values
                row_as_bytes.extend(value_as_bytes)
        return row_as_bytes
    

    def deserialize_row(self, row_bytes: bytes) ->dict:
        row = {}
        offset = 0
        
        for column_name, column_info in self.schema.items():
            expected_type = column_info["type"]
            if expected_type == int: #if the column in this position in memory (byte storage) is meant to be an int in the table schema
                value = int.from_bytes(row_bytes[offset:offset+4], "big") #extract the next 4 bytes 
                offset += 4 # and move up 4 bytes in memory
            elif expected_type == str: #if its supposed to be a string
                length = int.from_bytes(row_bytes[offset:offset+4], "big") #get the length from the prefix we made earlier
                offset += 4 # and use this length to find where the value actually starts
                value = row_bytes[offset:offset+length].decode("utf-8") #extract that value
                offset += length # and move up that many bytes in memory
            elif expected_type == bool:
                value = bool(int.from_bytes(row_bytes[offset:offset+1], "big")) #if its bool, should just be 1 location that you move up in memory
                offset += 1
            else:
                raise TypeError(f"Unsupported type: {expected_type}")

            row[column_name] = value #assign this value to this column in the row

        return row #now you have the row after looping through all the columns and their types


