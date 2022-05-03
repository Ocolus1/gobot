from django.shortcuts import render
from datetime import datetime
from django.http import HttpResponse
from django.db import models
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import time
import random
import string
import json
from .utils import _start, _help, join_airdrop, _airdrop
from random import choices
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt


token = settings.TOKEN
# webhook_url = f"https://goblin.cypherspot.dev/telegram/{secret}/"
webhook_url = f"https://bf66-160-152-166-21.eu.ngrok.io/telegram/"
bot = telepot.Bot(token)
if webhook_url != bot.getWebhookInfo()['url']:
    bot.setWebhook(webhook_url)

def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1 style="color:red">Hello from my bot!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)



@csrf_exempt
def telegram(request):
    if request.method == "POST":
        if token:
            try:
                payload = json.loads(request.body.decode('utf-8'))
            except ValueError:
                return HttpResponseBadRequest('Invalid request body')
            try:
                chat_id = payload['message']['chat']['id']
                fname = payload["message"]["chat"]["first_name"]
                cmd = payload['message'].get('text') 
            except:
                chat_id = payload['callback_query']['from']['id']
                fname = payload['callback_query']['from']['first_name']
                cmd = payload['callback_query']['data']
            commands = {
                '/start': _start,
                '/help': _help,
                # '/sheldoncooper': _exports(chat_id),
            }
            try:
                if payload['message'].get('entities'):
                    if Command.objects.filter(chat_id=chat_id).exists():
                        comma = Command.objects.get(chat_id=chat_id)
                        comma.command = cmd.split()[0].lower()
                        comma.save()
                    else:
                        Command.objects.create(chat_id=chat_id, command=cmd.split()[0].lower())

            except:
                pass

            try:
                if Verification.objects.filter(chat_id=chat_id).exists():
                    pass
                else:
                    Verification.objects.create(chat_id=chat_id, verify="❌ Not verified")

                if cmd in ['setwallet', 'changewallet', 'settele',
                'changetele', 'settweet', 'changetweet',
                'tweetlink', 'setfacebook', 'changefacebook',
                'setinstagram', 'changeinstagram', 'setyoutube',
                'changeyoutube', 'setreddit', 'changereddit', 'verify'
                ]:
                    if Cmd.objects.filter(chat_id=chat_id).exists():
                        comma = Cmd.objects.get(chat_id=chat_id)
                        comma.cmd = cmd.split()[0].lower()
                        comma.save()
                    else:
                        Cmd.objects.create(chat_id=chat_id, cmd=cmd.split()[0].lower())
            except:
                pass
            func = commands.get(cmd.split()[0].lower()) 
            link = Link.objects.all()
            for lin in link:
                gen_c = lin.gen_c
                if func and cmd.endswith(gen_c):
                    if cmd.startswith('/start'):
                        command, pay = cmd.split(" ")
                        link = Link.objects.get(gen_c=pay)
                        chat = Link.objects.filter(chat_id=chat_id)
                        if link and not chat:
                            link.referral += 1
                            link.points += 200
                            link.save()
                            try:
                                bot.sendMessage(chat_id, func, parse_mode='Markdown')
                            except:
                                if Verification.objects.filter(chat_id=chat_id).exists():
                                    verify = Verification.objects.get(chat_id=chat_id)
                                    if verify.verify == "▶️ You have been Verified":
                                        key = InlineKeyboardMarkup(inline_keyboard=[
                                            [InlineKeyboardButton(text='⚜️ Join Airdrop ⚜️', callback_data='airdrop')],
                                        ])
                                        bot.sendMessage(chat_id, join_airdrop(fname), 
                                        reply_markup=key, parse_mode="Markdown")
                                    elif verify.verify == "❌ Not verified":
                                        key = InlineKeyboardMarkup(inline_keyboard=[
                                            [InlineKeyboardButton(text='⚜️ Verify Me ⚜️', callback_data='verify')],
                                        ])
                                        bot.sendMessage(chat_id, _start(fname),
                                            reply_markup=key, parse_mode="Markdown")
                                    # time.sleep(1)
                            # bot.sendMessage(chat_id, "You have been added to your referral")
                        elif link and chat:
                            bot.sendMessage(chat_id, "User already exist")
                        return JsonResponse({}, status=200)
                    return JsonResponse({}, status=200)
                elif cmd == "/start":
                    if Verification.objects.filter(chat_id=chat_id).exists():
                        verify = Verification.objects.get(chat_id=chat_id)
                        if verify.verify == "▶️ You have been Verified":
                            key = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='⚜️ Join Airdrop ⚜️', callback_data='airdrop')],
                            ])
                            # key = ReplyKeyboardRemove(remove_keyboard=True)
                            bot.sendMessage(chat_id, join_airdrop(fname), 
                            reply_markup=key, parse_mode="Markdown")
                        elif verify.verify == "❌ Not verified":
                            key = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='⚜️ Verify Me ⚜️', callback_data='verify')],
                            ])
                            bot.sendMessage(chat_id, _start(fname),
                                reply_markup=key, parse_mode="Markdown")
                elif cmd == "airdrop":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='⚜️ Submit Details ⚜️', callback_data='joined')],
                    ])
                    bot.sendMessage(chat_id, _airdrop(), 
                    reply_markup=key, parse_mode="Markdown")
                elif cmd == "verify":
                    if Verification.objects.filter(chat_id=chat_id).exists():
                        verify = Verification.objects.get(chat_id=chat_id)
                        if verify.verify == "▶️ You have been Verified":
                            msg = "▶️ You're a verified user"
                            bot.sendMessage(chat_id, msg, parse_mode="Markdown")
                        elif verify.verify == "❌ Not verified":
                            x , y = rand_m()
                            ver = x + y
                            verify.ver = ver
                            verify.save()
                            msg = f"*Your verification question is:* \n \n *What is {x} + {y} ?*"
                            bot.sendMessage(chat_id, msg, parse_mode="Markdown")
                            
                elif cmd == "joined" or cmd == "🔙Back":
                    check = check_joined(chat_id)
                    if check == "▶️ Refer and Earn GOB!":
                        key = ReplyKeyboardMarkup(keyboard=[
                            [
                                KeyboardButton(text="💰 Balance"),
                            ],
                            [
                                KeyboardButton(text="👫 Referral"),
                                KeyboardButton(text="⚙️Set wallet"),
                            ],
                            [
                                KeyboardButton(text="💬 Social Media"),
                                KeyboardButton(text="💥 Top 10"),
                            ],
                        ],
                            resize_keyboard = True
                        )
                        bot.sendMessage(chat_id, "▶️ Refer and Earn GOB!", 
                        reply_markup=key, parse_mode="Markdown")
                        
                        
                    elif check == "❌ Must join all channel":
                        bot.sendMessage(chat_id, "❌ Must join all channel", 
                        parse_mode="Markdown")
                elif cmd == "⚙️Set wallet":
                    if Ethaddress.objects.filter(chat_id=chat_id).exists():
                        eth = Ethaddress.objects.get(chat_id=chat_id)
                        add = eth.address
                        msg = (f"""
                            *Account Settings ⚙️ \n \n🤴 User : {fname} \n🆔 User ID : {chat_id} \nWallet : {add}*
                        """)
                        key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Change wallet address ✏️', callback_data='changewallet')],
                        ])
                        bot.sendMessage(chat_id , msg, reply_markup=key, parse_mode='Markdown')
                    else :
                        msg = (f"""
                            *Account Settings ⚙️ \n \n🤴 User : {fname} \n🆔 User ID : {chat_id} \nWallet : You have not set your wallet address*
                        """)
                        key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set wallet ✏️', callback_data='setwallet')],
                        ])
                        bot.sendMessage(chat_id , msg, reply_markup=key, parse_mode='Markdown')
                elif cmd == "setwallet" or cmd == "changewallet":
                    msg = "*✏️Send your BSC wallet address*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "💰 Balance":
                    if Link.objects.filter(chat_id=chat_id).exists():
                        link = Link.objects.get(chat_id=chat_id)
                        msg = f"🤴 User : {link.fname} \n \n 💰 Balance : {link.points} points"
                        bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                    else:
                        msg = "*Set Wallet Address and Fill your social media info to get your balance*"
                        bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "👫 Referral":
                    bot.sendMessage(chat_id, _mylink(chat_id, fname), parse_mode='Markdown')
                elif cmd == "💥 Top 10":
                    bot.sendMessage(chat_id, _top(chat_id), parse_mode='Markdown')
                elif cmd == "💬 Social Media":
                    key = ReplyKeyboardMarkup(keyboard=[
                            [
                                KeyboardButton(text="📞Telegram"),
                                KeyboardButton(text="💬Twitter"),
                            ],
                            [
                                KeyboardButton(text="📱Facebook"),
                                KeyboardButton(text="📷Instagram"),
                            ],
                            [
                                KeyboardButton(text="☎️Youtube"),
                                KeyboardButton(text="🖊️Reddit"),
                            ],
                            [
                                KeyboardButton(text="🔙Back"),
                            ],
                        ],
                            resize_keyboard = True
                    )
                    msg = "*Welcome to the social media menu*"
                    bot.sendMessage(chat_id , msg, reply_markup=key, parse_mode='Markdown')
                elif cmd == "📞Telegram":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='settele')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changetele')],
                    ])
                    bot.sendMessage(chat_id , _mytele(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "settele" or cmd == "changetele":
                    msg = "*Input your telegram username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "💬Twitter":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='settweet')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changetweet')],
                            [InlineKeyboardButton(text='Set Tweet link ✏️', callback_data='tweetlink')],
                    ])
                    bot.sendMessage(chat_id , _mytwitter(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "settweet" or cmd == "changetweet":
                    msg = "*Input your twitter username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "tweetlink":
                    msg = "*Input your twitter username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "📱Facebook":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='setfacebook')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changefacebook')],
                    ])
                    bot.sendMessage(chat_id , _myfacebook(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "setfacebook" or cmd == "changefacebook":
                    msg = "*Input your Facebook username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "📷Instagram":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='setinstagram')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changeinstagram')],
                    ])
                    bot.sendMessage(chat_id , _myinstagram(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "setinstagram" or cmd == "changeinstagram":
                    msg = "*Input your Instagram username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "☎️Youtube":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='setyoutube')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changeyoutube')],
                    ])
                    bot.sendMessage(chat_id , _myyoutube(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "setyoutube" or cmd == "changeyoutube":
                    msg = "*Input your Youtube username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "🖊️Reddit":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='setreddit')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changereddit')],
                    ])
                    bot.sendMessage(chat_id , _myreddit(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "setreddit" or cmd == "changereddit":
                    msg = "*Input your Reddit username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif func and not cmd.endswith(gen_c):
                    try:
                        bot.sendMessage(chat_id, func, parse_mode='Markdown')
                    except:
                        bot.sendMessage(chat_id, func(), parse_mode='Markdown')
                else:
                    if Cmd.objects.filter(chat_id=chat_id).exists():
                        comma = Cmd.objects.get(chat_id=chat_id)
                        if comma.cmd == "setwallet":
                            bot.sendMessage(chat_id, _ethaddress_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "verify":
                            verify = Verification.objects.get(chat_id=chat_id)
                            if cmd == str(verify.ver):
                                if Verification.objects.filter(chat_id=chat_id).exists():
                                    verify = Verification.objects.get(chat_id=chat_id)
                                    verify.verify = "▶️ You have been Verified"
                                    verify.save()
                                msg = "▶️ You have been Verified"
                                bot.sendMessage(chat_id, msg, parse_mode="Markdown")
                                key = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='⚜️ Joined ⚜️', callback_data='joined')],
                                ])
                                bot.sendMessage(chat_id, _start(fname),
                                    reply_markup=key, parse_mode="Markdown")
                            else:
                                msg = "❌ Not verified"
                                bot.sendMessage(chat_id, msg, parse_mode="Markdown")
                        elif comma.cmd == "changewallet":
                            bot.sendMessage(chat_id, _changeeth_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "settele":
                            bot.sendMessage(chat_id, _tele_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changetele":
                            bot.sendMessage(chat_id, _changetele_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "settweet":
                            bot.sendMessage(chat_id, _twitter_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changetweet":
                            bot.sendMessage(chat_id, _changetwitter_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "tweetlink":
                            bot.sendMessage(chat_id, _changetwitterlink_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "setfacebook":
                            bot.sendMessage(chat_id, _facebook_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changefacebook":
                            bot.sendMessage(chat_id, _changeface_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "setinstagram":
                            bot.sendMessage(chat_id, _instagram_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changeinstagram":
                            bot.sendMessage(chat_id, _changeinsta_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "setyoutube":
                            bot.sendMessage(chat_id, _youtube_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changeyoutube":
                            bot.sendMessage(chat_id, _changetube_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "setreddit":
                            bot.sendMessage(chat_id, _reddit_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changereddit":
                            bot.sendMessage(chat_id, _changereddit_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        else:
                            bot.sendMessage(chat_id, error_msg)
                return JsonResponse({}, status=200)
            # Only to use at the begining
            else:
                if cmd == "/start":
                    if Verification.objects.filter(chat_id=chat_id).exists():
                        verify = Verification.objects.get(chat_id=chat_id)
                        if verify.verify == "▶️ You have been Verified":
                            key = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='⚜️ Join Airdrop ⚜️', callback_data='airdrop')],
                            ])
                            bot.sendMessage(chat_id, join_airdrop(fname), 
                            reply_markup=key, parse_mode="Markdown")
                        elif verify.verify == "❌ Not verified":
                            key = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='⚜️ Verify Me ⚜️', callback_data='verify')],
                            ])
                            bot.sendMessage(chat_id, _start(fname),
                                reply_markup=key, parse_mode="Markdown")
                elif cmd == "verify":
                    if Verification.objects.filter(chat_id=chat_id).exists():
                        verify = Verification.objects.get(chat_id=chat_id)
                        if verify.verify == "▶️ You have been Verified":
                            msg = "▶️ You're a verified user"
                            bot.sendMessage(chat_id, msg, parse_mode="Markdown")
                        elif verify.verify == "❌ Not verified":
                            x , y = rand_m()
                            ver = x + y
                            verify.ver = ver
                            verify.save()
                            msg = f"*Your verification question is:* \n \n *What is {x} + {y} ?*"
                            bot.sendMessage(chat_id, msg, parse_mode="Markdown")
                elif cmd == "joined" or cmd == "🔙Back":
                    check = check_joined(chat_id)
                    if check == "▶️ Refer and Earn GOB!":
                        key = ReplyKeyboardMarkup(keyboard=[
                            [
                                KeyboardButton(text="💰 Balance"),
                            ],
                            [
                                KeyboardButton(text="👫 Referral"),
                                KeyboardButton(text="⚙️Set wallet"),
                            ],
                            [
                                KeyboardButton(text="💬 Social Media"),
                                KeyboardButton(text="💥 Top 10"),
                            ],
                        ],
                            resize_keyboard = True
                        )
                        bot.sendMessage(chat_id, "▶️ Refer and Earn GOB!", 
                        reply_markup=key, parse_mode="Markdown")
                    elif check == "❌ Must join all channel":
                        bot.sendMessage(chat_id, "❌ Must join all channel", 
                        parse_mode="Markdown")
                elif cmd == "⚙️Set wallet":
                    if Ethaddress.objects.filter(chat_id=chat_id).exists():
                        eth = Ethaddress.objects.get(chat_id=chat_id)
                        add = eth.address
                        msg = (f"""
                            *Account Settings ⚙️ \n \n🤴 User : {fname} \n🆔 User ID : {chat_id} \nWallet : {add}*
                        """)
                        key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Change wallet address ✏️', callback_data='changewallet')],
                        ])
                        bot.sendMessage(chat_id , msg, reply_markup=key, parse_mode='Markdown')
                    else :
                        msg = (f"""
                            *Account Settings ⚙️ \n \n🤴 User : {fname} \n🆔 User ID : {chat_id} \nWallet : You have not set your wallet address*
                        """)
                        key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set wallet ✏️', callback_data='setwallet')],
                        ])
                        bot.sendMessage(chat_id , msg, reply_markup=key, parse_mode='Markdown')
                elif cmd == "setwallet" or cmd == "changewallet":
                    msg = "*✏️Send your BSC wallet address*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "💰 Balance":
                    if Link.objects.filter(chat_id=chat_id).exists():
                        link = Link.objects.get(chat_id=chat_id)
                        msg = f"🤴 User : {link.fname} \n \n 💰 Balance : {link.points} points"
                        bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                    else:
                        msg = "*Set Wallet Address and Fill your social media info to get your balance*"
                        bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "👫 Referral":
                    bot.sendMessage(chat_id, _mylink(chat_id, fname), parse_mode='Markdown')
                elif cmd == "💥 Top 10":
                    bot.sendMessage(chat_id, _top(chat_id), parse_mode='Markdown')
                elif cmd == "💬 Social Media":
                    key = ReplyKeyboardMarkup(keyboard=[
                            [
                                KeyboardButton(text="📞Telegram"),
                                KeyboardButton(text="💬Twitter"),
                            ],
                            [
                                KeyboardButton(text="📱Facebook"),
                                KeyboardButton(text="📷Instagram"),
                            ],
                            [
                                KeyboardButton(text="☎️Youtube"),
                                KeyboardButton(text="🖊️Reddit"),
                            ],
                            [
                                KeyboardButton(text="🔙Back"),
                            ],
                        ],
                            resize_keyboard = True
                    )
                    msg = "*Welcome to the social media menu*"
                    bot.sendMessage(chat_id , msg, reply_markup=key, parse_mode='Markdown')
                elif cmd == "📞Telegram":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='settele')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changetele')],
                    ])
                    bot.sendMessage(chat_id , _mytele(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "settele" or cmd == "changetele":
                    msg = "*Input your telegram username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "💬Twitter":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='settweet')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changetweet')],
                            [InlineKeyboardButton(text='Set Tweet link ✏️', callback_data='tweetlink')],
                    ])
                    bot.sendMessage(chat_id , _mytwitter(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "settweet" or cmd == "changetweet":
                    msg = "*Input your twitter username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "tweetlink":
                    msg = "*Input your twitter username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "📱Facebook":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='setfacebook')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changefacebook')],
                    ])
                    bot.sendMessage(chat_id , _myfacebook(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "setfacebook" or cmd == "changefacebook":
                    msg = "*Input your Facebook username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "📷Instagram":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='setinstagram')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changeinstagram')],
                    ])
                    bot.sendMessage(chat_id , _myinstagram(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "setinstagram" or cmd == "changeinstagram":
                    msg = "*Input your Instagram username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "☎️Youtube":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='setyoutube')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changeyoutube')],
                    ])
                    bot.sendMessage(chat_id , _myyoutube(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "setyoutube" or cmd == "changeyoutube":
                    msg = "*Input your Youtube username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "🖊️Reddit":
                    key = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Set Username ✏️', callback_data='setreddit')],
                            [InlineKeyboardButton(text='Change Username ✏️', callback_data='changereddit')],
                    ])
                    bot.sendMessage(chat_id , _myreddit(chat_id), reply_markup=key, parse_mode='Markdown')
                elif cmd == "setreddit" or cmd == "changereddit":
                    msg = "*Input your Reddit username*"
                    bot.sendMessage(chat_id, msg, parse_mode='Markdown')
                elif cmd == "👫 Referral":
                    bot.sendMessage(chat_id, _mylink(chat_id, fname), parse_mode='Markdown')
                elif func :
                    try:
                        bot.sendMessage(chat_id, func, parse_mode='Markdown')
                        # bot.sendMessage(chat_id, "halo3", parse_mode='Markdown')
                    except:
                        bot.sendMessage(chat_id, func(), parse_mode='Markdown')
                else:
                    if Cmd.objects.filter(chat_id=chat_id).exists():
                        comma = Cmd.objects.get(chat_id=chat_id)
                        if comma.cmd == "setwallet":
                            bot.sendMessage(chat_id, _ethaddress_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "verify":
                            verify = Verification.objects.get(chat_id=chat_id)
                            if cmd == str(verify.ver):
                                if Verification.objects.filter(chat_id=chat_id).exists():
                                    verify = Verification.objects.get(chat_id=chat_id)
                                    verify.verify = "▶️ You have been Verified"
                                    verify.save()
                                msg = "▶️ You have been Verified"
                                bot.sendMessage(chat_id, msg, parse_mode="Markdown")
                                key = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='⚜️ Joined ⚜️', callback_data='joined')],
                                ])
                                bot.sendMessage(chat_id, _start(fname),
                                    reply_markup=key, parse_mode="Markdown")
                            else:
                                msg = "Get your 👫 Referral link first."
                                bot.sendMessage(chat_id, msg, parse_mode="Markdown")
                        elif comma.cmd == "changewallet":
                            bot.sendMessage(chat_id, _changeeth_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "settele":
                            bot.sendMessage(chat_id, _tele_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changetele":
                            bot.sendMessage(chat_id, _changetele_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "settweet":
                            bot.sendMessage(chat_id, _twitter_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changetweet":
                            bot.sendMessage(chat_id, _changetwitter_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "tweetlink":
                            bot.sendMessage(chat_id, _changetwitterlink_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "setfacebook":
                            bot.sendMessage(chat_id, _facebook_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changefacebook":
                            bot.sendMessage(chat_id, _changeface_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "setinstagram":
                            bot.sendMessage(chat_id, _instagram_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changeinstagram":
                            bot.sendMessage(chat_id, _changeinsta_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "setyoutube":
                            bot.sendMessage(chat_id, _youtube_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changeyoutube":
                            bot.sendMessage(chat_id, _changetube_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "setreddit":
                            bot.sendMessage(chat_id, _reddit_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        elif comma.cmd == "changereddit":
                            bot.sendMessage(chat_id, _changereddit_cn(chat_id, cmd.split()[0].lower()), parse_mode='Markdown')
                        else:
                            bot.sendMessage(chat_id, error_msg)
            return JsonResponse({}, status=200)
        else :
            return HttpResponseForbidden('Invalid token')


class Cmd(models.Model):
    chat_id = models.IntegerField(default=0)
    cmd = models.CharField(max_length=400)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.chat_id}'

class Verification(models.Model):
    chat_id = models.IntegerField(default=0)
    verify = models.CharField(max_length=400, default="❌ Not verified")
    ver = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.chat_id}'

class Command(models.Model):
    chat_id = models.IntegerField(default=0)
    command = models.CharField(max_length=400)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.chat_id}'

class Email(models.Model):
    chat_id = models.IntegerField(default=0)
    email = models.EmailField(max_length=400)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Telegram(models.Model):
    chat_id = models.IntegerField(default=0)
    username = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Tweet(models.Model):
    chat_id = models.IntegerField(default=0)
    username = models.CharField(max_length=100)
    tw_link = models.CharField(max_length=400, default="mytweetlink")
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Facebook(models.Model):
    chat_id = models.IntegerField(default=0)
    username = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Instagram(models.Model):
    chat_id = models.IntegerField(default=0)
    username = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Youtube(models.Model):
    chat_id = models.IntegerField(default=0)
    username = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Reddit(models.Model):
    chat_id = models.IntegerField(default=0)
    username = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Ethaddress(models.Model):
    chat_id = models.IntegerField(default=0)
    address = models.CharField(max_length=100)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

class Link(models.Model):
    chat_id = models.CharField(max_length=400, unique=True)
    twitter = models.CharField(max_length=400, default="tweetuser")
    telegram = models.CharField(max_length=400, default="teleuser")
    facebook = models.CharField(max_length=400, default="facebookuser")
    instagram = models.CharField(max_length=400, default="instagramuser")
    youtube = models.CharField(max_length=400, default="youtubeuser")
    reddit = models.CharField(max_length=400, default="reddituser")
    ethaddress = models.CharField(max_length=400, default="ethuser")
    fname = models.CharField(max_length=400)
    gen_c = models.CharField(max_length=400, unique=True)
    points = models.IntegerField(default=0)
    referral = models.IntegerField(default=0)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.chat_id}'

    def __init__(self, *args, **kwargs):
        super(Link, self).__init__(*args, **kwargs)
        if self.gen_c:
            pass
        else:
            self.gen_c = self.generate_short_link()    
        
    def generate_short_link(self):
        characters = string.digits + string.ascii_letters
        gen_c = "".join(choices(characters, k=8))

        if Link.objects.filter(gen_c=gen_c).exists():
            return self.generate_short_link()

        return gen_c

    def save(self, *args, **kwargs):
        self.telegram = Telegram.objects.get(chat_id=self.chat_id).username
        self.twitter = Tweet.objects.get(chat_id=self.chat_id).username
        self.facebook = Facebook.objects.get(chat_id=self.chat_id).username
        self.instagram = Instagram.objects.get(chat_id=self.chat_id).username
        self.youtube = Youtube.objects.get(chat_id=self.chat_id).username
        self.reddit = Reddit.objects.get(chat_id=self.chat_id).username
        self.ethaddress = Ethaddress.objects.get(chat_id=self.chat_id).address
        super(Link, self).save(*args, **kwargs)
        
# 1070834749 Duke_of_python


def _help():
    return """
/start - start
Not a recognised command - Say What?
👫 Referral - Simple refer and earn!
💰Balance - Do tasks and earn!
"""

# func that sends msg to the usr
def send_msg(chat_id, msg_text):
    response = bot.sendMessage(chat_id, msg_text)
    return response

def check_joined(chat_id):
    channel = "@goblinHonter"
    try:
        check = bot.getChatMember(chat_id=channel, user_id=chat_id)
        if check['status'] == "member" or check['status'] == "creator":
            return "▶️ Refer and Earn GOB!"
        else:
            return "❌ Must join all channel"
    except telepot.exception.TelegramError as e:
        return "❌ Must join all channel"

def rand_m():
    x = random.randint(1, 10)
    y = random.randint(1, 10)
    return x, y

# Telegram
def _mytele(chat_id):
    chat_id = chat_id
    if Telegram.objects.filter(chat_id=chat_id).exists(): 
        result = Telegram.objects.get(chat_id=chat_id)
        user = result.username
        tot = "*🤴 Your username - {} *".format(user)
        return tot
    else:
        msg = "*You do not have a telegram handle.*"
        return msg

def _tele_cn(chat_id, text):
    try:
        if Telegram.objects.filter(chat_id=chat_id).exists():
            return "*You've already set up your username*"
        else:
            Telegram.objects.create(chat_id=chat_id, username=text)
    except:
        return "*An error occurred.*"
    return "Telegram Username is saved"

def _changetele_cn(chat_id, text):
    try:
        result = Telegram.objects.get(chat_id=chat_id)
        result.username =  text
        result.save()
    except:
        return "An error occurred"
    return "Telegram Username is saved"

#twitter
def _mytwitter(chat_id):
    chat_id = chat_id
    if Tweet.objects.filter(chat_id=chat_id).exists(): 
        result = Tweet.objects.get(chat_id=chat_id)
        user = result.username
        tot = "*🤴 Your username - {} *".format(user)
        return tot
    else:
        msg = "*You do not have a twitter handle.*"
        return msg

def _twitter_cn(chat_id, text):
    try:
        if Tweet.objects.filter(chat_id=chat_id).exists():
            return "*You've already set up your username*"
        else:
            Tweet.objects.create(chat_id=chat_id, username=text)
    except:
        return "*An error occurred.*"
    return "Twitter Username is saved"

def _changetwitter_cn(chat_id, text):
    try:
        result = Tweet.objects.get(chat_id=chat_id)
        result.username =  text
        result.save()
    except:
        return "An error occurred"
    return "Twitter Username is saved"

def _changetwitterlink_cn(chat_id, text):
    try:
        result = Tweet.objects.get(chat_id=chat_id)
        result.tw_link =  text
        result.save()
    except:
        return "An error occurred"
    return "Your retweet link is saved"

# Facebook
def _myfacebook(chat_id):
    chat_id = chat_id
    if Facebook.objects.filter(chat_id=chat_id).exists(): 
        result = Facebook.objects.get(chat_id=chat_id)
        user = result.username
        tot = "*🤴 Your username - {}*".format(user)
        return tot
    else:
        msg = "*You do not have a facebook handle.*"
        return msg

def _facebook_cn(chat_id, text):
    try:
        if Facebook.objects.filter(chat_id=chat_id).exists():
            return "*You've already set up your username*"
        else:
            Facebook.objects.create(chat_id=chat_id, username=text)
    except:
        return "*An error occurred.*"
    return "Facebook Username is saved"

def _changeface_cn(chat_id, text):
    try:
        result = Facebook.objects.get(chat_id=chat_id)
        result.username =  text
        result.save()
    except:
        return "An error occurred"
    return "Facebook Username is saved"

# Instagram
def _myinstagram(chat_id):
    chat_id = chat_id
    if Instagram.objects.filter(chat_id=chat_id).exists(): 
        result = Instagram.objects.get(chat_id=chat_id)
        user = result.username
        tot = "*🤴 Your username - {} *".format(user)
        return tot
    else:
        msg = "*You do not have a instagram handle.*"
        return msg

def _instagram_cn(chat_id, text):
    try:
        if Instagram.objects.filter(chat_id=chat_id).exists(): 
            return "*You've already set up your username*"
        else:
            Instagram.objects.create(chat_id=chat_id, username=text)
    except:
        return "*An error occurred*"
    return "Instagram Username is saved"

def _changeinsta_cn(chat_id, text):
    try:
        result = Instagram.objects.get(chat_id=chat_id)
        result.username =  text
        result.save()
    except:
        return "An error occurred"
    return "Instagram Username is saved"

# Youtube
def _myyoutube(chat_id):
    chat_id = chat_id
    if Youtube.objects.filter(chat_id=chat_id).exists(): 
        result = Youtube.objects.get(chat_id=chat_id)
        user = result.username
        tot = "*🤴 Your username - {} *".format(user)
        return tot
    else:
        msg = "*You do not have a youtube handle.*"
        return msg

def _youtube_cn(chat_id, text):
    try:
        if Youtube.objects.filter(chat_id=chat_id).exists(): 
            return "*You've already set up your username*"
        else:
            Youtube.objects.create(chat_id=chat_id, username=text)
    except:
        return "*An error occurred*"
    return "Youtube Username is saved"

def _changetube_cn(chat_id, text):
    try:
        result = Youtube.objects.get(chat_id=chat_id)
        result.username =  text
        result.save()
    except:
        return "An error occurred"
    return "Youtube Username is saved"

# Reddit
def _myreddit(chat_id):
    chat_id = chat_id
    if Reddit.objects.filter(chat_id=chat_id).exists(): 
        result = Reddit.objects.get(chat_id=chat_id)
        user = result.username
        tot = "*🤴 Your username - {} .*".format(user)
        return tot
    else:
        msg = "*You do not have a reddit handle.*"
        return msg

def _reddit_cn(chat_id, text):
    try:
        if Reddit.objects.filter(chat_id=chat_id).exists(): 
            return "*You've already set up your username*"
        else:
            Reddit.objects.create(chat_id=chat_id, username=text)
    except:
        return "*An error occurred*"
    return "Reddit Username is saved"

def _changereddit_cn(chat_id, text):
    try:
        result = Reddit.objects.get(chat_id=chat_id)
        result.username =  text
        result.save()
    except:
        return "An error occurred"
    return "Reddit Username is saved"


# Bsc address
def _ethaddress_cn(chat_id, text):
    try:
        if Ethaddress.objects.filter(chat_id=chat_id).exists():
            return "*You've already set up your username*"
        else:
            Ethaddress.objects.create(chat_id=chat_id, address=text)
    except:
        return "*An error occurred.*"
    return "*Wallet Address is saved*"

def _changeeth_cn(chat_id, text):
    try:
        result = Ethaddress.objects.get(chat_id=chat_id)
        result.address = text
        result.save()
    except:
        return "An error occurred"
    return "*Wallet Address is saved*"


# the referral link
def _mylink(chat_id, fname):
    chat_id = chat_id
    fname = fname
    if Link.objects.filter(chat_id=chat_id).exists():
        links = Link.objects.get(chat_id=chat_id)
        msg = f"*⏯️ Total Invites er: {links.referral} User(s)\n \n ⛔️ Earn 2 GOB per refferal! \n \n 🔗 Referral Link ⬇️\n https://telegram.me/godsrebornbot?start={links.gen_c} *"
        return msg
    else:
        try:
            Link.objects.create(chat_id=chat_id, fname=fname)
        except:
            return "*Set Wallet Address and Fill your social media info to get your link*"
        lin = Link.objects.get(chat_id=chat_id)
        msg = f"*⏯️ Total Invites rt: {lin.referral} User(s)\n \n ⛔️ Earn 2 GOB per refferal! \n \n 🔗 Referral Link ⬇️\n https://telegram.me/godsrebornbot?start={lin.gen_c}*"
        # send_msg(chat_id, msg)
        return msg

def _top(chat_id):
    # link = Link.query.order_by(Link.referral.desc()).all()
    link = Link.objects.order_by("-referral")
    for lin in link[:10]:
        return str(lin.fname) + " " + str(lin.referral)

    return "*You haven't gotten your referral link yet*"



# def _exports(chat_id):
#     # link = db.engine.execute('SELECT * FROM link')
#     link = Link.objects.all()
#     with open("wub.csv", "w") as csv_file:
#         fieldnames = ['id', 'chat_id', 'email', 'twitter', 'telegram',
#         'facebook', 'ethaddress', 'fname', 'gen_c', 'referral', 'pub_date']
#         writer = csv.writer(csv_file)
#         writer.writerow(fieldnames)
#         for lin in link:
#             writer.writerow(lin)
#     msg =  "file exported to wub\\.csv"
#     return msg


error_msg= """
❌ Unknown Command!

You have send a Message directly into the Bot's chat or
Menu structure has been modified by Admin.

ℹ️ Do not send Messages directly to the Bot or
reload the Menu by pressing /start
"""