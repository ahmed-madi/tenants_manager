## Tenants Manager

Multi-Tenants Systems Manager


## Main DocTypes to work with:

`Business Owner`
> DocType to Save Business Owners Details!

`Site Subscription`
> DocType to Save Business Owners Subscription!

`Site Subscription Security`
> DocType store Administrator passwords for each site (Subscription).

`Site Subscription Action Log`
> Main docType that track all actions that applies on `Site Subscription`

`Business Site Settings`
> A single DocType to Set basic config.

`Error Log`
> Core frappe DocType to check all errors while sites creations



#### License

mit

### End point to test
> /api/method/tenants_manager.api.business.apply

> #### Register a new `Business Owner`

> POST data
```
{
  "first_name": "john",
  "last_name": "Do",
  "email_address": "j@domain.com",
  "phone_number": "+00056666666",
  "date_of_birth": "2005-12-19",

  "business_type": "Enterprise",
  "business_legal_name": "Toman",
  "business_id": "06695887",
  
  "address_line_1": "Add 1, st1",
  "address_line_2": "Add 2, 0366",
  "city": "My City",
  "state": "State",
  "zip_code": "000",
  "country": "Ukraine"
}

```
