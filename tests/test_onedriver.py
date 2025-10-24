


def test_print_title(a_context): 
    its_web = a_context.web
    a_context.load(its_web)
    a_context.execute_query()
    print("Web title: {0}".format(its_web.properties['Title']))



