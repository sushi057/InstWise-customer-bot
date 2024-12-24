from fastapi import APIRouter, HTTPException
from schemas.outreach import (
    GenerateEmailReplyRequest,
    GenerateEmailReplyResponse,
    SendEmailRequest,
    SendEmailResponse,
)

router = APIRouter()


@router.post("/email-replies", response_model=GenerateEmailReplyResponse)
async def generate_email_reply(request: GenerateEmailReplyRequest):
    """
    Generate an email reply to a customer.
    """
    return GenerateEmailReplyResponse(
        email_body="""
To add breakfast to a hotel reservation using the StaynTouch application, please follow these steps:

Start a New Reservation:

Create a new reservation in the StaynTouch application.
Select Room and Rate:

Choose a room type and rate combination from the Rooms and Rates screen.
Enhance Stay:

On the Enhance Stay page, you'll see a list of top-selling add-ons. You can also explore different options on the left side of the screen for more add-ons.
Find Breakfast Add-On:

Look for the breakfast add-on in the list of available enhancements.
Select Quantity:

Choose the number of breakfasts you would like to add to your reservation.
Add Breakfast:

Click the "ADD" button to include breakfast in your hotel reservation.
Room Enhancements Dialog:

A "ROOM ENHANCEMENTS" dialog will appear with options to "ADD MORE TO THIS ROOM" or "CLOSE WINDOW." If you want to add more enhancements, choose "ADD MORE TO THIS ROOM"; otherwise, click "CLOSE WINDOW."
Confirm Reservation:

Finally, proceed by clicking the green "BOOK" button to confirm the addition of breakfast to your hotel reservation.
Please let me know if you need further assistance or if there's anything else I can help you with!
 """
    )


@router.post("/send-email", response_model=list[SendEmailResponse])
async def send_email(request: SendEmailRequest):
    """
    Send an email to a customer.
    """
    responses = [
        SendEmailResponse(
            email_from="sushilbhattachan@gmail.com",
            email_to="sarah@hilton.com",
            subject="Noticed a decline in login activity",
            email_body="""
Hi Sarah,

I hope this message finds you well.

I’ve noticed a recent decline in login activity and wanted to check in to see if there’s anything we can assist you with. If you’re facing any challenges using our application or if there’s anything preventing you from fully utilizing it, please don’t hesitate to reach out.

We’re here to help and ensure you have a smooth experience with our platform.

Looking forward to hearing from you.

Best regards,
Sushil Bhattachan
""",
        ),
        SendEmailResponse(
            email_from="sushilbhattachan@gmail.com",
            email_to="david@hyatt.com",
            subject="Assistance with Auto Face Recognition for Check in",
            email_body="""
Hi Sarah,

I hope you’re doing well.

I noticed that the Auto Face Recognition feature for check-in has not been actively utilized recently. I wanted to check if there’s any assistance we can provide to help you or your team leverage this feature effectively.

If there are any challenges or questions regarding its setup or usage, please feel free to let us know. We’re here to ensure you get the most out of this functionality and have a seamless experience.

Looking forward to your response.

Best regards,
Sushil Bhattachan
""",
        ),
    ]

    return responses
