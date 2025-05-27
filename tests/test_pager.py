from storage import Page
import pytest
from constants import PAGE_SIZE


def test_get_page_from_pager():
        
    # create a test file
    test_file = "test_data.db"

    # create a page that says hello
    page = Page(page_id = 0)
    page.add_value(b'hello')
    # write that page to the file as bytes
    raw_bytes = page.to_bytes()
    with open(test_file,'wb') as f:
        f.write(raw_bytes)

    # now find this value in the file

    # create a pager with this test file
    pager = Pager(file_path = test_file)
    page = pager.get_page(page_id=0)
    assert page.values[0] == b'hello'




def test_write_page_to_disk():
    # create a test file and make a pager instance with it
    test_file = "test_data.db"
    pager = Pager(test_file)

    # create a page and add a value
    page = Page(page_id = 0)
    page.add_value(b'hello')
    # insert the page into the pager's cache
    pager.cache[0] = page
    # insert page into dirty set
    pager.dirty_pages.add(page.page_id)
    # write the page to the disk
    pager.write_page(0)
    # read what is in the file (pager's cache) 
    with open(test_file, 'rb') as f:
        read_data = f.read(PAGE_SIZE)
        f.close()

    # confirm that read_data is the same as the cache you just wrote to it 
    # assert that the page is now in the file
    assert page.to_bytes() == read_data


# page_ids need to be incremented otherwise they don't get created
def test_number_of_pages_created():

    test_file = "test_data.db"
    # create a pager
    pager = Pager(test_file)

    # Page 0 with some data
    page0 = Page(page_id=0)
    # add value and push it to cache and add to dirty list
    page0.add_value(b'hello')
    pager.cache[0] = page0
    pager.dirty_pages.add(0)
    pager.write_page(0)

    # skip pages 1 and 2 to test if they still get created
    page3 = Page(page_id=3)
    # add value and push it to cache and add to dirty list
    page3.add_value(b'bye')
    pager.cache[3] = page3
    pager.dirty_pages.add(3)
    pager.write_page(3)

    # File size should be at least 4 * PAGE_SIZE bytes
    expected_file_size = (3 + 1) * PAGE_SIZE
    actual_file_size = os.path.getsize(test_file)

    assert actual_file_size >= expected_file_size