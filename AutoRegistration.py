from McGillRegistrationBot import McGillRegistrationBot
from apscheduler.schedulers.blocking import BlockingScheduler

courseInfo = (
    {
        "term": "202109",
        "subject": "MATH",
        "number": "324",
        "section": "001"
    },
    {
        "term": "202109",
        "subject": "COMP",
        "number": "360",
        "section": "001"
    },
    {
        "term": "202109",
        "subject": "ECON",
        "number": "306",
        "section": "001"
    },
    {
        "term": "202109",
        "subject": "COMP",
        "number": "445",
        "section": "001"
    },
    {
        "term": "202201",
        "subject": "COMP",
        "number": "302",
        "section": "001"
    },
{
        "term": "202201",
        "subject": "COMP",
        "number": "303",
        "section": "001"
    },
    {
        "term": "202201",
        "subject": "COMP",
        "number": "310",
        "section": "001"
    },
    {
        "term": "202201",
        "subject": "COMP",
        "number": "421",
        "section": "001"
    },
    {
        "term": "202201",
        "subject": "ENVR",
        "number": "202",
        "section": "001"
    },
    {
        "term": "202109",
        "subject": "COMP",
        "number": "417",
        "section": "001"
    },
)

bot = McGillRegistrationBot(courseInfo)

def start():
    bot.start()

schedule = BlockingScheduler()
#schedule.add_job(make_trade, 'interval', minutes=5)
schedule.add_job(start, 'cron', hour="08", minute="00", second="01")
schedule.start()

#bot.start()