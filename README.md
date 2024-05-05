# AWS_Checker_TeleBot
This is a simple Telegram Bot for checking the status of AWS Services. The current version can let you use for checking status of your own Lambda Functions. In the future, it will be able to check VPC, EC2 and so on, or even support more users.

The purpose of building this bot is to let me know more about the AWS services. If you are loooking for how to build your TeleBot with multiple functions, this project might give you some ideas. If you are a begginer, [this](https://github.com/ki225/telegram_bot_with_AWS_for_beginner.git) might suit for you.


## Scrrenshots
Here are the screenshots of using this bot.

<img src="img/IMG_1281.jpg" width="225" height="400" /> <img src="img/IMG_1282.PNG" width="225" height="400" /> <img src="img/IMG_1285.JPG" width="225" height="400" /> <img src="img/IMG_1286.JPG" width="225" height="400" />

## How to set your own checker bot with this repo?
1. Create an EC2
2. Connect your local host to the EC2 with SSH
3. Put the python file into your EC2 host
The path I set the python file is in the directory `/home/ec2-user/checker_bot`.
4. Prepare all the package you need
In the EC2 you create, it is a whole new environment without the resources you need. First, we need the "pip" package. If you remember that you downloaded it before, you can check it by using `pip --version` first.
```
sudo yum upgrade
sudo yum -y install python-pip
```
Then we can download the packages we need for the python file with "pip install" command.
```
pip install telebot
pip install boto3
pip install matplotlib
```
You can run the python code with "python checker_bot.py" to check whether all the packages are set completely.

5. Let the bot know WHO YOU ARE
You have to set the "AWS configuration" with your AWS access key, secret access key and region. Use the command below for setting. Otherwise, the bot will not catch the information for you like the following screenshot.

<img width="953" alt="截圖 2024-05-05 上午9 24 07" src="https://github.com/ki225/AWS_Checker_TeleBot/assets/123147937/75854aa6-cfdd-4db8-bbdc-13e9b3696617">

```
aws configure
```

6. Use "nohup"
For serving consistently, the python code have to keep running for getting user message no matter whether the EC2 console is open. 
```
nohup python3 checker_bot.py
```
If you set some check point or error handler like try/except, you can check them from "nohup.out" with the command below.
```
tail -f nohup.out
``` 
7. Congrat!

## Handler
Values of the global variable "HANDLER" represent the next input will give to which function. 
- 0 : Start of this bot, just give some hint for the user.
- 1x : Check for Lambda Function
- 2x : Check for VPC
- x0 : choose the target one from all of your Lambda Functions or VPCs
- x1 : Choose the service by clicking buttons
- x2 : Count the numbers of error from CLoudWatch and Draw the error chart
- x3 : Get all log streams in the target log group
- x4 : Get detail in the target stream

### CLoudWatch
If you want your TeleBot give you more information, you can grab the data from CLoudWatch. I use the data from CLoudWatch for counting how many errors happened in my Lambda Function.

<img width="1497" alt="截圖 2024-05-04 下午1 39 51" src="https://github.com/ki225/AWS_Checker_TeleBot/assets/123147937/0cf732df-23dd-4756-9679-f01d5542e4b0">

You have to use the function `get_metric_data` for getting the data. Here are the documents you might need:
- [get_metric_statistics](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch/client/get_metric_statistics.html)
- [get_metric_data](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch/client/get_metric_data.html)

The document clearly explain all the parameters in this function. You can find the value corresponding to the parameter like below:

<img width="1497" alt="截圖 2024-05-05 上午9 23 07" src="https://github.com/ki225/AWS_Checker_TeleBot/assets/123147937/e1759573-9644-45c3-995e-74f282bc6954">

