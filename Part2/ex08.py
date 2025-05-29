speed_limit = 60.0


print(f"The speed limit is {speed_limit}.")

while True:
    user_speed = input('What speed are you going? ')
    if user_speed.isdigit():
        user_speed = float(user_speed)
        break
    else:
        print('Not a valid speed.')

if user_speed > speed_limit:
    print("You are going over the speed limit.")
elif user_speed < speed_limit:
    print("You are going under the speed limit.")
elif user_speed == speed_limit:
    print("You are going exactly at the speed limit!")