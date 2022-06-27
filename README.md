# Valio - Progressive Validation Library. 
Validation that goes along with  dataclasses

<a href="https://pypi.org/project/valio" target="_blank">
    <img src="https://img.shields.io/pypi/v/valio?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

## Installation

<div class="termy">

```console
$ pip install valio
---> 100%
Successfully installed valio
```

## Example
  
</div>
  
```python 
from dataclasses import dataclass
import bcrypt
import valio
from valio import (StringValidator,
                    AadhaarCardValidator, 
                    PhoneNumberValidator, 
                    EmailIDValidator, 
                    PaymentCardValidator, 
                    DateValidator, 
                    Validator,
                    PatternValidator)

# firstly we create a User class for various field validations.

@dataclass
class User(object):
   name: str = StringValidator(logger=False, debug=True, max_length=50, required=True)
   aadhaar: str = AadhaarCardValidator(logger=False, debug=True)
   phone: str = PhoneNumberValidator(logger=False, debug=True)
   email: str = EmailIDValidator(logger=False, debug=True, reassign=False)
   credit_card: str = PaymentCardValidator(logger=False, debug=True)
   date: datetime.datetime = DateValidator(logger=False, debug=True, default=datetime.datetime.utcnow)
   gender: str = Validator(in_choice=["Male", "Female", "Trans"], default="Female")

# if logger=True, the field is logged in a separate file. if debug=True, any wrong type/valued entry 
# throws an error in console else it defaults to None.

# now we can create the UserValidator itself that validates the User class.
valio.Validator.register(User)  # noqa

class UserValidator(valio.Validator):
    annotation = typing.Union[User, None]

# this UserValidator can be directly used or used further to create a UserField

class UserField(valio.Field):
    validator = UserValidator
    
# now we can use pre and post validation with this field.

@dataclass
class RegisterUser(object):
    user_field = UserField(logger=False, debug=True)
    password_field = valio.StringField(
        min_length=6,
        max_length=30,
        debug=True,
        required=True
    )
    confirm_password_field = valio.StringField(
        min_length=6,
        max_length=30,
        debug=True,
        required=True
    )
    
    @user_field.add_pre_valiator
    def user_not_in_db(self, user: User):
        # logic goes here....
        
    @user_field.add_post_validator
    async def email_user_activity(self, user: User):
        # async logic to email that user has signed up...
        
    @password_field.add_validator
    def one_small_char(self, value: str):
        try:
            PatternValidator(pattern=Pattern(r"[a-z]", count_min=1)).validate(value=value)
        except Exception:
            raise ValueError(f"{self.password_field} must have at least one small character")
        return value

    @password_field.add_validator
    def one_capital_char(self, value: str):
        try:
            PatternValidator(pattern=Pattern(r"[A-Z]", count_min=1)).validate(value=value)
        except Exception:
            raise ValueError(f"{self.password_field} must have at least one capital character")
        return value

    @password_field.add_validator
    def one_digit_char(self, value: str):
        try:
            PatternValidator(pattern=Pattern(r"\d", count_min=1)).validate(value=value)
        except Exception:
            raise ValueError(f"{self.password_field} must have at least one integer character")
        return value

    @password_field.add_post_validator
    def encrypt_password(self, password: str) -> bytes:
        try:
            password = password.encode("utf-8")
        except (Exception,):
            pass
        return bcrypt.hashpw(password, bcrypt.gensalt())

    @confirm_password_field.add_post_validator
    def encrypt_confirm_password(self, confirm_password: str) -> bytes:
        try:
            confirm_password = confirm_password.encode("utf-8")
        except (Exception,):
            pass
        return bcrypt.hashpw(confirm_password, self.password)
        
     user: User = user_field.validator
     password: str = password_field.validator
     confirm_password: str = confirm_password_field.validator
    
user = User(name="....", ...) 

# if user contains invalid values and debug is True on any field, it throws an error for all those debugged fields.

```

## Regex 
Valio supports regex too out of the box.

```python 
from valio import Pattern, StartOfString, WordBoundary
from pyparsing import Regex

hyphen = Pattern(r"-", alias="-")
colon = Pattern(r":", alias=":")
backslash = Pattern(r"/", alias="/")
space = Pattern(r"\s", count_min=0, greedy=False, alias=" ")
four_digits = space & Pattern(r"\d", count=4, alias="dddd") & space
two_digits = space & Pattern(r"\d", count=2, alias="dd") & space

# European Date Format
eu_date_with_hyphen = four_digits & hyphen & two_digits & hyphen & two_digits
eu_date_with_colon = four_digits & colon & two_digits & colon & two_digits
eu_date_with_backslash = four_digits & backslash & two_digits & backslash & two_digits
eu_date = WordBoundary(eu_date_with_colon | eu_date_with_hyphen | eu_date_with_backslash)

# Indian Date format
ind_date_with_hyphen = two_digits & hyphen & two_digits & hyphen & four_digits
ind_date_with_colon = two_digits & colon & two_digits & colon & four_digits
ind_date_with_backslash = two_digits & backslash & two_digits & backslash & four_digits
ind_date = WordBoundary(ind_date_with_hyphen | ind_date_with_colon | ind_date_with_backslash)

start_str = StartOfString(space & Pattern("date") & space & colon & space)
date_ = (start_str & eu_date) | (start_str & ind_date)

print(date_.alias)
print(date_.pattern)
print(Regex(date_.pattern).re_match("date  : 2021:01:20"))
print(Regex(date_.pattern).re_match("date: 2021/01/20"))
print(Regex(date_.pattern).re_match("date : 01-20-2021112"))

```

