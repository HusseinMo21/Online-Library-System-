import resend

# حط الـ API Key هنا مباشرة أو خليه ييجي من env
resend.api_key = "re_cCYvZkn2_LEs4YotdnayVnPN45segESAo"

def send_email(to_email, subject, html):
    return resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to_email,
        "subject": subject,
        "html": html,
    })
