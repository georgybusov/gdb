from storage import Page
import pytest

# check if we can make an empty page
def test_page_init_empty():
    page = Page(page_id=1)
    assert page.page_id == 1
    assert page.max_size == 4096
    assert page.current_size == 0
    assert page.values == []
    assert page.deleted_indices == set()

# Single value add
def test_add_value_once():
    # instantiate a page and add value into it
    page = Page(page_id=2)
    data = b"testing"
    row_id = page.add_value(data)
    # this value should be in first row
    assert row_id == 0
    assert page.values == [data]
    # Size should be 4 (prefix) + 7 (string)
    assert page.current_size == 11


# Bring the added values back
def test_get_value_valid():
    # instantiate a page and add value into it
    page = Page(page_id=3)
    data = b"hello"
    row_id = page.add_value(data)
    
    assert page.get_value(row_id) == data

# try getting a value that was never added to page
def test_get_value_invalid():
    page = Page(page_id=4)

    with pytest.raises(IndexError):
        page.get_value(0)


# deleting a value
def test_delete_value_basic():
    # instantiate a page and add value into it
    page = Page(page_id=5)
    data = b"hello"
    row_id = page.add_value(data)
    # delete value at that row
    page.delete_value(row_id)

    # should gotten sent to deleted_infeces
    assert row_id in page.deleted_indices
    # Value is None
    assert page.values[row_id] is None
    # Size is back to empty
    assert page.current_size == 0


# delete something invalid
def test_delete_value_invalid():
    # instantiate a page
    page = Page(page_id=6)
    # delete the same thing twice
    row_id = page.add_value(b"test")
    page.delete_value(row_id)
    # delete a row that doesn't exist
    with pytest.raises(IndexError):
        page.delete_value(row_id)
    # delete a value that doesn't exist
    with pytest.raises(IndexError):
        page.delete_value(99)


# Make sure add_value reuses deleted row ids
def test_add_reuses_deleted_slot():
    # instantiate a page and add value into it
    page = Page(page_id=7)
    a = page.add_value(b"apple")
    # delete the value and add a new one
    page.delete_value(a)
    b = page.add_value(b"banana")
    # a and b should be the same values because we reuse slots
    assert b == a
    assert page.values[b] == b"banana"


# Test serializing to bytes and then loading back from it
def test_serialize_and_deserialize():
    # instantiate a page and add value into it
    page = Page(page_id=8)
    page.add_value(b"dog")
    page.add_value(b"cat")
    # add 2 values and delete the first
    page.delete_value(0)
    # serialize the page
    raw_bytes = page.to_bytes()
    new_page = Page.from_bytes(page_id=99, raw=raw_bytes)
    # The second value should be preserved
    assert new_page.get_value(1) == b"cat"
    # The first value should be deleted
    with pytest.raises(IndexError):
        new_page.get_value(0)
    # current_size shoud be 1 only (delete before serialization)
    assert new_page.current_size == len(b"cat") + 4


# What if we try to stuff too much into a page?
def test_add_too_much_data():
    page = Page(page_id=10, max_size=20)
    # Assuming our max_size is 20, anything over 20 wouldn't fit (same with anything over 4KB in real example)
    with pytest.raises(ValueError):
        page.add_value(b"123456789123456789123456789123456789")


# test invalid input when instantiating a page
def test_from_bytes_incomplete_value():
    # byte stream is length of 50 but only gives 2 (simulating incomplete input)
    raw = (50).to_bytes(4, 'big') + b'hi'
    page = Page.from_bytes(page_id=11, raw=raw)
    # should not load at all 
    assert page.values == []
    assert page.current_size == 0
