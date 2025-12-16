<h3>Hello,,</h3>

<p>You registered an account on portal, before being able to use your account you need to verify that this is your email address by using the code below.</p>

<p><b>{{ doc.otp_code }}</b></p>

<p>Or Simply click the big blue button below to verify your email address.</p>

<div><a style="display: block;
    width: 115px;
    height: 25px;
    background: #4E9CAF;
    padding: 10px;
    text-align: center;
    border-radius: 5px;
    color: white;
    font-weight: bold;
    line-height: 25px;
" href="http://54.205.212.182/api/business/{{doc.business_owner_id}}/wizard/verify-email-link?hash_code={{otp_link_hash}}&otp_code={{doc.otp_code}}">Verfiy Now</a></div>

<p>Kind Regards,</p>
