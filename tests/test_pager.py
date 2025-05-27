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