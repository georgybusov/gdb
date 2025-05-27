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