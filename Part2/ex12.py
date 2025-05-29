def check_string(Yes_No):
    if Yes_No.startswith("The"):
        return "Yes!"
    else:
        return "No!"

str1 = 'The'
str2 = 'Thumbs up'
str3 = 'Theatre can be boring'

print(check_string(str1))
print(check_string(str2))
print(check_string(str3))