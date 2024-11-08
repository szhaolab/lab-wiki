# Script to login to discovery automatically

Everytime we login to discovery, we will have to enter our password. In the following tutorial, we will write a script that allow us to avoid typing password each time we log in.

In mac, open terminal and enter the directory you want to save this script. (Usually to minimize the number of steps, we can store this script under the root directory `~`.) Create a new file `login.expect`, and then open this file.

For example, on our lab computer:
```
szhaolab@Szhaos-Mac-mini ~ % touch login.expect
szhaolab@Szhaos-Mac-mini ~ % vim login.expect
```

Then press `i` to insert the following content:
```
#!/usr/bin/expect

set timeout 10

spawn ssh <your_dartmouth_ID>@discovery.dartmouth.edu

expect "<your_dartmouth_ID>@discovery.dartmouth.edu's password:"

send "<your_password>\r"

interact
```

Replace `<your_dartmouth_ID>` with your Dartmouth ID. \
Replace `<your_password>` with your Dartmouth password.

Then write and quit this file by first pressing `esc`, and then typing `:wq`.

Now run this script using `expect` and you will be able to login to discovery without typing password everytime.
```
szhaolab@Szhaos-Mac-mini ~ % expect login.expect
```

You only need to run this script using `expect login.expect` everytime you want to login to discovery (no need to write it again unless you changed the password). Please only save this script on computer you trust, since the password is not confidential.