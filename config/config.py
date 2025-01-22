from typing import TypedDict


class CustomerInfo(TypedDict):
    customer_id: str | None
    customer_email: str | None


CUSTOMER_INFO: CustomerInfo = {
    "customer_id": None,
    "customer_email": None,
}


def get_customer_info() -> CustomerInfo:
    global CUSTOMER_ID
    return CUSTOMER_INFO


def set_customer_info(customer_info: CustomerInfo) -> CustomerInfo:
    global CUSTOMER_INFO

    CUSTOMER_INFO = customer_info
    return CUSTOMER_INFO


if __name__ == "__main__":
    print(get_customer_info())
