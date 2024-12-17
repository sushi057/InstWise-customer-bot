CUSTOMER_ID = None


def get_customer_id():
    global CUSTOMER_ID
    return CUSTOMER_ID


def set_customer_id(customer_id):
    global CUSTOMER_ID
    CUSTOMER_ID = customer_id
    return CUSTOMER_ID
