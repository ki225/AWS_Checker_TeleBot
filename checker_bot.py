import telebot
from telebot import types
import boto3
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
from io import BytesIO

# ==================== global variable ==============================
TOKEN = <TELEGRAM_BOT_TOKEN> 
AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION = "", "", ""
lambda_client = None
LAMBDA_FUNCTION_NAME = ""
HANDLER = 0
bot = telebot.TeleBot(TOKEN)

# ==================== lambda info functions ==============================
# 14
def get_detail_in_the_stream(log_stream_name, chat_id):
    global HANDLER
    client = boto3.client('logs', region_name=AWS_REGION)
    response = client.get_log_events(
        logGroupName= "/aws/lambda/" + LAMBDA_FUNCTION_NAME,
        logStreamName=log_stream_name,
        limit=10,  # max event number
        startFromHead=True  # from new to old
    )
    log_events = response['events']
    error_dict={}
    for each_event in log_events:
        if "[ERROR]" in each_event['message']:
            time_stamp = str(each_event['timestamp'])[0:2]+":"+str(each_event["timestamp"])[2:4]
            if time_stamp not in error_dict:
                error_dict[time_stamp]=1
            else:
                error_dict[time_stamp]+=1
    if len(error_dict) == 0:
        bot.send_message(chat_id, 'No error message in the log stream.')
    else:
        bot.send_message(chat_id, 'Here is/are error message(s) in the log stream you want to check: ')
        for k,v in error_dict.items():
            bot.send_message(chat_id, f"At {k} there is/are {v} error(s).")
            print(f"At {k} there is/are {v} error(s).")
    HANDLER = 0

# ========================= Error chart =========================
# data from CLoudWatch
# 12
def error_chart(Y1, M1, D1, Y2, M2, D2, chat_id):  
    
    global HANDLER  
    cloudwatch_client = boto3.client('cloudwatch')

    response = cloudwatch_client.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'errors',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/Lambda',
                        'MetricName': 'Errors',
                        # 'Dimensions': [
                        #     {
                        #         'Name': 'mytelebot3',
                        #         'Value': 'string'
                        #     },
                        # ]
                    },
                    'Period': 3600*3, #  multiple of 60.
                    'Stat': 'Sum',
                    # 'Unit': 'Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None'
                },
                # 'Expression': 'string',
                # 'Label': 'string',
                # 'ReturnData': True|False,
                # 'Period': 123,
                # 'AccountId': 'string'
            },
        ],
        StartTime=datetime(2024, 5, 3),
        EndTime=datetime(2024, 5, 4),
        ScanBy='TimestampDescending',
        LabelOptions={
            'Timezone': "+0800" # UTC +8hr
        }
    )

    # draw the chart
    x = ["x"]+[date.strftime("%y/%m/%d %H:%M") for date in response["MetricDataResults"][0]["Timestamps"]][::-1]
    y = [0]+(response["MetricDataResults"][0]["Values"])[::-1]
    
    plt.figure().set_figwidth(15)
    plt.plot(x, y)
    plt.xlabel('time')
    plt.ylabel('error-count')
    plt.title('error-count in the last 7 days')
    plt.savefig("img2.png")
    bot.send_message(chat_id, f"Total errors in the last 7 days: {sum(response['MetricDataResults'][0]['Values'])}")
    plt.savefig("img.png", dpi = 100)
    bot.send_photo(chat_id, open("img2.png", 'rb'))
    plt.show()
    bot.send_message(chat_id, f"You can click /functions to choose another service you want to check: ")
    HANDLER = 0


# ==================================================

# 13
def get_all_log_streams_in_group(limit_day, chat_id):
    global HANDLER, LAMBDA_FUNCTION_NAME
    logGroupName = "/aws/lambda/" + str(LAMBDA_FUNCTION_NAME)
    client = boto3.client('logs', region_name=AWS_REGION)
    response = client.describe_log_streams(
        logGroupName=logGroupName,
        orderBy='LastEventTime',  # sort by time
        descending=True,  # new -> old
    )
    bot.send_message(chat_id, 'Here is/are the log stream(s) in the log group you want to check: ')
    count = 0
    print(response['logStreams'])
    for stream in response['logStreams']:
        print(stream['logStreamName'][:10])
        if stream['logStreamName'][2:10] == limit_day[2:]:
            count+=1
            bot.send_message(chat_id, stream['logStreamName'])
            print(stream['logStreamName'])
    if count == 0:
        bot.send_message(chat_id, 'No log stream in the date you want to check.')
    HANDLER = 13
    bot.send_message(chat_id, 'Please enter the another date you want to check or click /functions for another service: ')

def checking(chat_id):
    global HANDLER, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION
    if HANDLER == 10:
        bot.send_message(chat_id, 'Here are the list of lambda functions:')
        try:
            lambda_client = boto3.client('lambda', region_name=AWS_REGION)
            response = lambda_client.list_functions()
            i=1
            for function in response['Functions']:
                bot.send_message(chat_id, f"function{i}: {function['FunctionName']}")
                i+=1
            bot.send_message(chat_id, "choose the function you want to check: ")
            HANDLER = 11
        except:
            bot.send_message(chat_id, 'Something went wrong, please try again.')
        lambda_client = boto3.client('lambda', region_name=AWS_REGION)



# ==================== telegram bot functions ==============================
# /lambda_func
@bot.message_handler(commands=['check_which'])
def check_which(message):
    keyboard = types.InlineKeyboardMarkup()
    button_lambda = types.InlineKeyboardButton(text='lambda func', callback_data='lambda_func')
    button_vpc = types.InlineKeyboardButton(text='vpc', callback_data='vpc')
    keyboard.add(button_lambda, button_vpc)
    bot.send_message(message.chat.id, 'Click the button', reply_markup=keyboard)

@bot.message_handler(commands=['functions'])
def check_which(message):
    keyboard2 = types.InlineKeyboardMarkup()
    button_error_chart = types.InlineKeyboardButton(text='error chart', callback_data='error_chart')
    button_log_stream_in_group = types.InlineKeyboardButton(text='log_stream_in_group', callback_data='log_stream_in_group')
    button_detail_in_log_stream = types.InlineKeyboardButton(text='detail_in_log_stream', callback_data='detail_in_log_stream')
    keyboard2.add(button_error_chart, button_log_stream_in_group, button_detail_in_log_stream)
    bot.send_message(message.chat.id, 'Click the button', reply_markup=keyboard2)

# click the button
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global HANDLER
    if call.data == 'lambda_func':
        bot.send_message(call.message.chat.id, 'Please enter your Region: ') #'Please enter your AWS_Access_Key/AWS_Secret_Access_Key/Region(use space to seperate them) : '
        HANDLER = 10
    elif call.data == 'vpc':
        HANDLER = 20
        bot.send_message(call.message.chat.id, 'Here is the status of the vpc:')
    elif call.data == 'error_chart':
        bot.send_message(call.message.chat.id, 'How long ago do you want to check the log? Please input YYYY/MM/DD ~ YYYY/MM/DD')
        HANDLER = 12
    elif call.data == 'log_stream_in_group':
        bot.send_message(call.message.chat.id, 'Please enter the date you want to check the log stream(YYYY/MM/DD): ')
        HANDLER = 13
    elif call.data == 'detail_in_log_stream':
        bot.send_message(call.message.chat.id, 'Please enter the name of the log stream you want to check: ')
        HANDLER = 14

# get user input
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, HANDLER, LAMBDA_FUNCTION_NAME, LAMBDA_FUNCTION_NAME
    print(f"message are {message.text}")
    print(f"handler are {HANDLER}")
    if HANDLER == 0:
        bot.send_message(message.chat.id, 'Hello, I am a bot for checking your AWS service\nPlease enter /check_which to choose the service you want to check (>.-)')
    elif HANDLER == 10 or HANDLER == 20:
        AWS_REGION = message.text.strip()
        checking(message.chat.id)
    elif HANDLER == 11:
        LAMBDA_FUNCTION_NAME = message.text.strip()
        bot.send_message(message.chat.id, 'Please click /functions to choose the service you want to check (>.-)')
    elif HANDLER == 12:
        bot.send_message(message.chat.id, 'Here is the error chart:')
        try:
            Y1, M1, D1 = message.text.split(' ')[0].split('/')
            Y2, M2, D2 = message.text.split(' ')[2].split('/')
            error_chart(int(Y1), int(M1), int(D1), int(Y2), int(M2), int(D2), message.chat.id)
        except:
            bot.send_message(message.chat.id, 'The input is not correct, please start the service again.')
    elif HANDLER == 13:   
        try:
            date = message.text.strip()
            bot.send_message(message.chat.id, 'Wait a minute, I am checking the status of the target lambda function...')
            get_all_log_streams_in_group(date, message.chat.id)
        except:
            bot.send_message(message.chat.id, 'The input is not correct, please start the service again.')
    elif HANDLER == 14:
        log_stream_name = message.text.strip()
        get_detail_in_the_stream(log_stream_name, message.chat.id)
    elif HANDLER == 20:
        bot.send_message(message.chat.id, 'Here is the status of the vpc:')
    else: 
        bot.send_message(message.chat.id, 'Hello, I am a bot for checking your AWS service\nPlease enter /check_which to choose the service you want to check (>.-)')

# ========================= start the bot =========================
bot.polling()
