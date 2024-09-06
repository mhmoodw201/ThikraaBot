import pytz
#from datetime import time
from datetime import datetime, timedelta
from datetime import date
from pyIslam.praytimes import (
    PrayerConf,
    Prayer,
    #LIST_FAJR_ISHA_METHODS,
)
#from pyIslam.hijri import HijriDate
#from pyIslam.qiblah import Qiblah     
from hijridate import Gregorian #,Hijri
from turtle import update
import logging
#from telegram import InlineKeyboardButton, KeyboardButton
from telegram import Update
#from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Application, CommandHandler, ContextTypes, CallbackContext, filters  # Add MessageHandler import
#from telegram.ext import 
from timezonefinder import TimezoneFinder


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

####################################################################################################### دالة للحصول على مواقيت الصلاة

# الدالة لمعالجة الموقع المشارك
async def handle_location(update: Update, context: CallbackContext) -> None:
    global latitude
    global longitude
    global utc_offset
    global initialize_location  # Add this line to reference the global variable
    #location = update.message.location
    initialize_location = InitializeLocation()
    chat_id = update.effective_message.chat_id
    
    if update.message.location:
        user_location = update.message.location
        initialize_location.set_location(user_location.longitude, user_location.latitude)
        latitude = initialize_location.latitude
        longitude = initialize_location.longitude
        await update.message.reply_text("تم تحديد المنطقة الزمنية وأوقات الصلاة في مدينتك بنجاح")
        #await update.message.reply_text(f' تم الوصول لنقاط : خط الطول = {initialize_location.longitude}, خط العرض = {initialize_location.latitude}')
        
        # تحديد المنطقة الزمنية بناءً على الإحداثيات
        tz_finder = TimezoneFinder()
        timezone_str = tz_finder.timezone_at(lat=initialize_location.latitude, lng=initialize_location.longitude)
        tz = pytz.timezone(timezone_str)
        
        if timezone_str is None:
            raise ValueError("Could not determine the timezone for the given coordinates.")
    
        # الحصول على المنطقة الزمنية باستخدام pytz
        tz = pytz.timezone(timezone_str)
    
        # الحصول على الوقت الحالي في المنطقة الزمنية المحددة
        now = datetime.now(tz)
    
        # الحصول على الرقم الزمني (UTC offset) بالثواني وتحويله إلى ساعات
        utc_offset = now.utcoffset().total_seconds() / 3600
        
        await update.message.reply_text("""
                                    مرحبا بك في بوت ذكرى \U0001f343
                                    تقدم لك أذكار وتذكير بالموعظة الحسنة، 
                                    مواقيت الصلاة بتوقيت جامعة أم القرى \U0001F54B
                                    
                                    1- للحصول على مواقيت الصلاة والتاريخ الهجري /time
                                    2- للحصول على اذكار الصباح /morning
                                    3- للحصول على اذكار المساء /evening
                                    4- لإيقاف البوت /stop
                                    5- للمساعدة /help

                                    بدأ الأن في تذكيرك برسائل تلقائية... \U0001F4C5
                                                                        """)
    

        # الحصول على الوقت المحلي
        #current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    else:
        await update.message.reply_text('رجاء قم بمشاركة موقعك لتحديد مواقيت الصلاة الصحيحة')


    context.job_queue.run_repeating(send_prayer_reminder, interval=60, first=0, chat_id=chat_id)
    context.job_queue.run_repeating(Athkar, interval=60, first=0, chat_id=chat_id)
    

"""
    # إرسال المعلومات للمستخدم
    update.message.reply_text(f"الإحداثيات:\n"
                              f"خط العرض: {latitude}\n"
                              f"خط الطول: {longitude}\n"
                              f"المنطقة الزمنية: {timezone_str}\n"
                              f"الوقت المحلي: {current_time}")
                              """

####################################################################################################### متغيرات البوت
class InitializeLocation:
    def __init__(self):
        self.longitude = None
        self.latitude = None

    def set_location(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

initialize_location = InitializeLocation()

async def initialize_location_handler(update: Update, context: CallbackContext) -> None:
    # Ensure that location_handler has been called and the global variables are set
    #await handle_location(update, context)

# Call the function to initialize location
    #await initialize_location_handler(update, context)

    #global long, lat, timezone, fajr_isha_method, asr_fiqh, pconf, pt
    long = longitude        #39.826168
    lat = latitude           #21.422510
    timezone = utc_offset
    fajr_isha_method = 4
    asr_fiqh = 1

    #global long, lat, timezone, fajr_isha_method, asr_fiqh, pconf, pt
    global pconf, pt
    pconf = PrayerConf(float(long), float(lat), float(timezone), fajr_isha_method, asr_fiqh)
    pt = Prayer(pconf, date.today())
    
"""
    prayer_times = {
       str(pt.fajr_time().strftime('%H:%M')),
       str(pt.sherook_time().strftime('%H:%M')),
       str(pt.dohr_time().strftime('%H:%M')),
       str(pt.asr_time().strftime('%H:%M')),
       str(pt.maghreb_time().strftime('%H:%M')),
       str(pt.ishaa_time().strftime('%H:%M')),
       str(pt.last_third_of_night().strftime('%H:%M'))}"""


x = Gregorian.today().to_hijri() 
c = x.datetuple()
ramadan_start = datetime(2025, 3, 3)  # Ramadan 2025 
today = datetime.now()
days_remaining = (ramadan_start - today).days

if days_remaining > 0:
    response = f"باقي على شهر رمضان {days_remaining} يوما"
elif days_remaining <= 0:
    response = """
       أن هذا اليوم هو أحدى أيام شهر رمضان المبارك
       رمضان كريم \U0001F319 
       """

####################################################################################################### اذكار الصباح والمساء

async def Athkar(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await initialize_location_handler(update, context)
    
    PRAYER = "الورد اليومي \U0001F343"
    
    MORNING_IMAGE_PATH = 'morning.png'
    MORNING_PRAYER = "أذكار الصباح \U0001F324"
    
    EVENING_IMAGE_PATH = 'evening.png'
    EVENING_PRAYER = "أذكار المساء \U0001F319"

    PDF_FILE_PATH = 'سورة الكهف.pdf'
    FILE_PATH = """
    من قرأ سورة الكهف في يوم الجمعة أضاء له من النور ما بين الجمعتين .. 
    
    {قَالَ اللَّهُ تَعَالَى: {إِنَّ اللَّهَ وَمَلَائِكَتَهُ يُصَلُّونَ عَلَى النَّبِيِّ يَا أَيُّهَا الَّذِينَ آمَنُوا صَلُّوا عَلَيْهِ وَسَلِّمُوا تَسْلِيمًا 
    اللهم صلي وسلم على نبينا محمد .. \U0001F343
    """

    current_time = datetime.now() + timedelta(minutes=30)

    try:
        if str(current_time.strftime('%H:%M')) == str(pt.sherook_time().strftime('%H:%M')): # اذكار الصباح
           with open(MORNING_IMAGE_PATH, 'rb') as photo:
              await context.bot.send_photo(job.chat_id, photo=photo, caption=MORNING_PRAYER)
        
        elif str(current_time.strftime('%H:%M')) == str(pt.maghreb_time().strftime('%H:%M')): # اذكار المساء
           with open(EVENING_IMAGE_PATH, 'rb') as photo:
              await context.bot.send_photo(job.chat_id, photo=photo,caption=EVENING_PRAYER)

        elif str(current_time.strftime('%H:%M')) == '00:00': # مواقيت الصلاة
            await context.bot.send_message(job.chat_id, text=f"""
        مواقيت الصلاة بتوقيتك المحلي \U0001F54B
               
        == \U0001F4C5 | يوم {x.day_name('ar')} تاريخ {c[2]} {x.month_name('ar')} {c[0]} هـ ==
            
        الفجر     : {pt.fajr_time().strftime("%I:%M %p")}
        الشروق  : {pt.sherook_time().strftime("%I:%M %p")}
        الظهر     : {pt.dohr_time().strftime("%I:%M %p")}
        العصر    : {pt.asr_time().strftime("%I:%M %p")}
        المغرب  : {pt.maghreb_time().strftime("%I:%M %p")}
        العشاء   : {pt.ishaa_time().strftime("%I:%M %p")}
             
        === \U0001F319 | {response} ===
                            
           """)

        elif str(current_time.strftime('%H:%M')) == '13:00' and str(x.day_name('ar')) == 'الجمعة': # اذكار يوم الجمعة
            with open(PDF_FILE_PATH, 'rb') as pdf_file:
                await context.bot.send_document(job.chat_id, document=pdf_file, caption=FILE_PATH)
        

        elif str(current_time.strftime('%H:%M')) == '18:00': # الورد اليومي
           for i in range(1, 605):  # يبدأ العد من 1 إلى 604
                IMAGE_PATH = f"{i:04}.jpg"
                with open(IMAGE_PATH, 'rb') as photo:
                    await context.bot.send_photo(job.chat_id, photo=photo,caption=PRAYER)
                i += 1
                if i == 604:
                    i = 1
                break
        
        #else:
            #await context.bot.send_message(job.chat_id, text="استغفر الله")

    except (IndexError, ValueError):
        await context.bot.send_message(job.chat_id, text="هناك خطأ ما في الاذكار ")


####################################################################################################### دالة لإرسال صورة ونص للمستخدم في موعد الصلاة

async def morning(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
        chat_id = update.effective_message.chat_id
        MORNING_IMAGE_PATH = 'morning.png'
        MORNING_PRAYER = "أذكار الصباح \U0001F324"
        with open(MORNING_IMAGE_PATH, 'rb') as photo:
              await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=MORNING_PRAYER)


async def evening(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
        chat_id = update.effective_message.chat_id
        EVENING_IMAGE_PATH = 'evening.png'
        EVENING_PRAYER = "أذكار المساء \U0001F319"
        with open(EVENING_IMAGE_PATH, 'rb') as photo:
              await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=EVENING_PRAYER)

####################################################################################################### دالة لإرسال رسالة للمستخدم في موعد الصلاة
async def send_prayer_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await initialize_location_handler(update, context)
    long = float(initialize_location.longitude)
    lat = float(initialize_location.latitude)
    timezone = utc_offset
    fajr_isha_method = 4
    asr_fiqh = 1

    pconf = PrayerConf(long, lat, timezone, fajr_isha_method, asr_fiqh)
    pt = Prayer(pconf, date.today())
    current_time =str(datetime.now().strftime('%H:%M'))


    if current_time == str(pt.fajr_time().strftime('%H:%M')):
        await context.bot.send_message(job.chat_id, text=""" حان الأن موعد صلاة الفجر \U0001F343
                                       حسب التوقيت المحلي \U0001F54B 
                                       
                                       """)
    elif current_time == str(pt.sherook_time().strftime('%H:%M')):
        await context.bot.send_message(job.chat_id, text=""" << أَوْصَانِي خَلِيلِي بثَلَاثٍ لا أدَعُهُنَّ حتَّى أمُوتَ: صَوْمِ ثَلَاثَةِ أيَّامٍ مِن كُلِّ شَهْرٍ، وصَلَاةِ الضُّحَى، ونَوْمٍ علَى وِتْرٍ. >> \U0001F319
                                       صلاة الضحى يا أحبة الله \U0001F343 \U0001F90D .. 
                                       
                                       """)
    elif current_time == str(pt.dohr_time().strftime('%H:%M')):
        await context.bot.send_message(job.chat_id, text=""" حان الأن موعد صلاة الظهر \U0001F343
                                       حسب التوقيت المحلي \U0001F54B 
                                       
                                       """)
    elif current_time == str(pt.asr_time().strftime('%H:%M')):
        await context.bot.send_message(job.chat_id, text=""" حان الأن موعد صلاة العصر \U0001F343
                                       حسب التوقيت المحلي \U0001F54B 
                                       
                                       """)
    elif current_time ==  str(pt.maghreb_time().strftime('%H:%M')):
        await context.bot.send_message(job.chat_id, text=""" حان الأن موعد صلاة المغرب \U0001F343
                                       حسب التوقيت المحلي \U0001F54B 
                                       
                                       """)
    elif current_time == str(pt.ishaa_time().strftime('%H:%M')):
        await context.bot.send_message(job.chat_id, text=""" حان الأن موعد صلاة العشاء \U0001F343
                                       حسب التوقيت المحلي \U0001F54B 
                                       
                                       """)
    elif current_time == str(pt.last_third_of_night().strftime('%H:%M')):
        await context.bot.send_message(job.chat_id, text=""" << أنَّ رَجُلًا سَأَلَ رَسولَ اللَّهِ صَلَّى اللهُ عليه وسلَّمَ عن صَلَاةِ اللَّيْلِ، فَقالَ رَسولُ اللَّهِ عليه السَّلَامُ: صَلَاةُ اللَّيْلِ مَثْنَى مَثْنَى، فَإِذَا خَشِيَ أحَدُكُمُ الصُّبْحَ صَلَّى رَكْعَةً واحِدَةً تُوتِرُ له ما قدْ صَلَّى >> \U0001F343
                                       أيها الأحبة في الله، تذكروا أن صلاة الوتر هي من صلوات الليل الموصى بها. لا تفوتوا فرصة القيام بها فهي خير وبركة وفرصة لتقرب إلى الله واستجابة الدعاء \U0001F343 \U0001F90D ..
                                       
                                       """)
    #else:
        #await context.bot.send_message(job.chat_id, text="لا يوجد مواعيد صلاة حاليا")

####################################################################################################### دالة لإيقاف البوت

async def stop(update: Update, context: CallbackContext) -> None:
    """إيقاف البوت."""
    await update.message.reply_text('البوت يتوقف الآن...')
    context.application.stop()

####################################################################################################### دالة لبدء البوت

async def start(update: Update, context: CallbackContext) -> None:

    #chat_id = update.effective_message.chat_id #update.message.chat_id #chat_id=chat_id
    
    await update.message.reply_text('\U0001F4CD حتى يمكننا البدء في تذكيرك، يرجى مشاركة موقعك معنا لتحديد مواقيت الصلاة الصحيحة - لا تقلق لن نستخدم موقعك لأي غرض آخر - ') 

async def help(update: Update, context: CallbackContext) -> None:
    
    await update.message.reply_text("""
                                    بوت ذكرى \U0001f343
                                    
                                    1- للحصول على مواقيت الصلاة والتاريخ الهجري /time
                                    2- للحصول على اذكار الصباح /morning
                                    3- للحصول على اذكار المساء /evening
                                    4- للتوقف عن تلقي الرسائل اليومية /stop
                                    5- للمساعدة /help
                                    6- لمشاركة موقعك /location
                                    
                                    ....
                                                                        """)

#################################################################################################### توقيت الصلاة
    
async def time_p(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ensure that location_handler has been called and the global variables are set
    await initialize_location_handler(update, context)

    # Initialize prayer times
    long = initialize_location.longitude
    lat = initialize_location.latitude
    timezone = utc_offset
    fajr_isha_method = 4
    asr_fiqh = 1

    pconf = PrayerConf(long, lat, timezone, fajr_isha_method, asr_fiqh)
    pt = Prayer(pconf, date.today())

    chat_id = update.effective_message.chat_id
    
    await context.bot.send_message(chat_id=chat_id, text=f"""
        مواقيت الصلاة بتوقيتك المحلي \U0001F54B
               
        == \U0001F4C5 | يوم {x.day_name('ar')} تاريخ {c[2]} {x.month_name('ar')} {c[0]} هـ ==
            
        الفجر     : {pt.fajr_time().strftime("%I:%M %p")}
        الشروق  : {pt.sherook_time().strftime("%I:%M %p")}
        الظهر     : {pt.dohr_time().strftime("%I:%M %p")}
        العصر    : {pt.asr_time().strftime("%I:%M %p")}
        المغرب  : {pt.maghreb_time().strftime("%I:%M %p")}
        العشاء   : {pt.ishaa_time().strftime("%I:%M %p")}
             
        === \U0001F319 | {response} ===
                            
           """)
    


############################################################################################ دالة البدء

def main() -> None:
    """Run bot."""
    application = Application.builder().token("6841337306:AAHYVamcFzzaQziaG8Pj4Gm6pYdqD6DiWQc").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start","location"], start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("time", time_p))
    application.add_handler(CommandHandler("morning", morning))
    application.add_handler(CommandHandler("evening", evening))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(CommandHandler("stop", stop))  # إضافة معالج الأمر stop
    #application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Start the scheduling in a separate thread
    #threading.Thread(target=schedule_jobs, daemon=True).start()

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

####################################################################################################### 
    """
    if update.message.location:
        user_location = update.message.location
        location_handler.set_location(user_location.longitude, user_location.latitude)
        update.message.reply_text(f'Location received: Longitude = {location_handler.longitude}, Latitude = {location_handler.latitude}')
    else:
        update.message.reply_text('Please send your location.')
    
    keyboard = [[InlineKeyboardButton("شارك موقعك", request_location=True)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('يرجى مشاركة موقعك:', reply_markup=reply_markup)
    """
    
    """
    context.job_queue.run_repeating(send_prayer_reminder, interval=60, first=0, chat_id=chat_id)
    context.job_queue.run_repeating(Athkar, interval=60, first=0, chat_id=chat_id)
    """
    #context.job_queue.run_repeating(job_evening, interval=60, first=0, chat_id=chat_id)
    #context.job_queue.run_repeating(prarytime, interval=60, first=0, chat_id=chat_id)
    #context.job_queue.run_once(start_reminders, 0, chat_id=chat_id)  #(hour=2, minute=46, second=0)
    # الاستخدام الصحيح لدالة time مع run_daily
    #context.job_queue.run_daily(job_morning, time=time(hour=4, minute=23, second=0), chat_id=chat_id)
    #context.job_queue.run_daily(job_evening, time=time(hour=4, minute=23, second=0), chat_id=chat_id) #=datetime.time(5,11,0)
    #context.job_queue.run_daily(prarytime, time=time(hour=4, minute=23, second=0), chat_id=chat_id)

"""
Simple Bot to send timed Telegram messages.

This Bot uses the Application class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

Note:
To use the JobQueue, you must install PTB via
`pip install "python-telegram-bot[job-queue]"`
"""

"""
print("Today's Prayer Times for Makkah")
print(f"==== شهر {x.month_name('ar')} يوم {x.day_name('ar')} | م{some_adhan.readable_timing(show_time=False)} - {x.dmyformat()}هـ ====")
for adhan in time:
    print("{: <15} | {: <15}".format(adhan.get_ar_name(), adhan.readable_timing(show_date=False)))
"""

# Define a few command handlers. These usually take the two arguments update and
# context.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.

"""
async def prarytime(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    current_time =str(datetime.now().strftime('%H:%M'))

    if current_time == '00:00':
        await context.bot.send_message(f"""
"""مواقيت الصلاة بتوقيت مكة المكرمة
               
        == \U0001F4C5 | يوم {x.day_name('ar')} تاريخ {c[2]} {x.month_name('ar')} {c[0]} هـ ==
            
        الفجر     : {pt.fajr_time().strftime("%I:%M %p")}
        الشروق  : {pt.sherook_time().strftime("%I:%M %p")}
        الظهر     : {pt.dohr_time().strftime("%I:%M %p")}
        العصر    : {pt.asr_time().strftime("%I:%M %p")}
        المغرب  : {pt.maghreb_time().strftime("%I:%M %p")}
        العشاء   : {pt.ishaa_time().strftime("%I:%M %p")}
             
        === \U0001F319 | {response} ===
                            
           )"""

"""
async def job_evening(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    EVENING_IMAGE_PATH = 'evening.png'
    EVENING_PRAYER = "أذكار المساء \U0001F319"
    current_time =datetime.now() + timedelta(minutes=20)

    try:
        if str(current_time.strftime('%H:%M')) == str(pt.maghreb_time().strftime('%H:%M')):
           with open(EVENING_IMAGE_PATH, 'rb') as photo:
              await context.bot.send_photo(job.chat_id, photo=photo,caption=EVENING_PRAYER)
        #await context.bot.send_message(job.chat_id, text=EVENING_PRAYER)
        #context.job_queue.run_daily(send_evening_prayer, time=datetime.time(hour=18, minute=0, second=0), context=chat_id)
        #await update.effective_message.reply_text(send_evening_prayer)

    except (IndexError, ValueError):
        await context.bot.send_message("هناك خطأ في الأمر - في مرحلة اذكار المساء")
"""

"""
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Sends explanation on how to use the bot.
    await update.message.reply_text()
"""
"""
async def start_reminders(context: CallbackContext) -> None:
    job = context.job
    for pray in prayer_times[pray]:
        await context.bot.send_message(job.chat_id, text=f"{send_prayer_reminder}") #text=f"Beep! {job.data} seconds are over!")
    #context.job_queue.run_repeating(send_prayer_reminder, interval=60, first=0, chat_id=job.chat_id, data=job.data)
"""
"""
async def jobp(context: CallbackContext) -> None:
    #job = context.job_queue.run_daily(callback, interval=5)
    #await job.run()
    #chat_id = update.effective_message.chat_id
    context.job_queue.run_daily(send_evening_prayer, time=datetime.time(hour=0, minute=0, second=0), chat_id=chat_id)
    #await update.effective_message.reply_text(time_p)
"""
"""
def schedule_jobs():
    # جدولة المهمة لتعمل كل يوم في الساعة 12 صباحًا
    schedule.every().day.at("04:07").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
"""
"""
async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Add a job to the queue.
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")
"""
"""
async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
# Send the alarm message.
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")
"""


"""
    for adhan in time:
        await update.message.reply_text("{:<15} | {:<15}".format(adhan.get_ar_name(), adhan.readable_timing(show_date=False)))
"""
