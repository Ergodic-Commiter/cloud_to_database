
from src import onedriver


def test_print_title(a_context): 
    its_web = a_context.web
    a_context.load(its_web)
    a_context.execute_query()
    print("Web title: {0}".format(its_web.properties['Title']))


def test_download_file(a_context, a_fileurl, local_path): 
    onedriver.download_from_sharepoint(a_context, a_fileurl, local_path)
    assert local_path.is_file, f"Couldn't download file from {a_fileurl}"


