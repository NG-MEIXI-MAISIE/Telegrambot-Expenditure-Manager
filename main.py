import telepot
import time
import urllib3
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop


# You can leave this bit out if you're using a paid PythonAnywhere account
proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))
# end of the stuff that's only needed for free accounts

bot = telepot.Bot('')

users = {}

def on_chat_message(raw_msg):
    content_type,chat_type, chat_id = telepot.glance(raw_msg)
    userId = raw_msg['from']['id']
    first_name = raw_msg['from']['first_name']
    if userId not in users:
        person=Person(userId, first_name)
        users.update({userId:person})


    if content_type == 'text':
        message = raw_msg["text"]

        if message == '/start':
                bot.sendMessage(chat_id, start_message)
                main_menu(chat_id)



        person = users[userId]
        if person.currentAction == 'Update':
            if not isNonNegativeFloat(message):
                bot.sendMessage(userId, 'Please enter a valid amount')
            else:
                amount = message
                person.account.update(person.currentCategory,amount)
                balanceMsg = 'Your current balance for ' + str(person.currentCategory) + ' has been updated.\nCurrent balance: ' + str(person.account.balance(person.currentCategory))
                bot.sendMessage(userId, balanceMsg)
                person.currentAction = 'NONE'






def on_callback_query(raw_msg):
    query_id, from_id, query_data = telepot.glance(raw_msg, flavor='callback_query')
    #print('Callback Query:', query_id, from_id, query_data)
    person = users[from_id]

    bot.answerCallbackQuery(query_id, text='Processing...')

    if query_data == 'Summary':
        bot.sendMessage(from_id, "This is a summary of your expenditure!")
        bot.sendMessage(from_id, person.account.summary())

    if query_data== 'View categories':
        person.currentAction = 'NONE'
        manage_categories(from_id)

    if query_data== 'Reset All':
        person.makeNone()
        person.account.reset_all()
        bot.sendMessage(from_id, 'Data has been reset!')





    categories=['Entertainment', 'Personal Care','Food and Dining','Auto and Transport','Investments or Debt Repayments','Miscellaneous','Savings']

    if query_data in categories:
        person.currentCategory = query_data
        list_of_actions(from_id)

    if query_data == 'Main Menu':
        person.makeNone()
        main_menu(from_id)

    if query_data == 'Update':
        person.currentAction = 'Update'
        bot.sendMessage(from_id, 'Please enter an amount.')

    if query_data=='Reset':
        person.currentAction='Reset'
        person.account.reset(person.currentCategory)
        resetMsg = 'Your current balance for ' + str(person.currentCategory) + ' has been reset to $0.'
        bot.sendMessage(from_id,resetMsg)




def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def isNonNegativeFloat(string):
    return isFloat(string) and not float(string)<0


def main_menu(chat_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Summary', callback_data='Summary')],
                [InlineKeyboardButton(text='View Categories', callback_data='View categories')],
                [InlineKeyboardButton(text='Reset All', callback_data='Reset All')]
                  ])

    bot.sendMessage(chat_id, 'Please pick one of the following.', reply_markup=keyboard)


def manage_categories(chat_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Entertainment', callback_data='Entertainment')],
                   [InlineKeyboardButton(text='Personal Care', callback_data='Personal Care')],
                   [InlineKeyboardButton(text='Food and Dining', callback_data='Food and Dining')],
                   [InlineKeyboardButton(text='Auto and Transport', callback_data='Auto and Transport')],
                   [InlineKeyboardButton(text='Investments or Debt Repayments', callback_data='Investments or Debt Repayments')],
                   [InlineKeyboardButton(text='Miscellaneous', callback_data='Miscellaneous')],
                   [InlineKeyboardButton(text='Savings', callback_data='Savings')]

                ] )

    bot.sendMessage(chat_id, 'Please choose a category.', reply_markup=keyboard)


def list_of_actions(chat_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Update', callback_data='Update')],
                   [InlineKeyboardButton(text='Reset', callback_data='Reset')],
                   [InlineKeyboardButton(text='Back to Categories', callback_data='View categories')],
                   [InlineKeyboardButton(text='Back to Main Menu', callback_data='Main Menu')]
                   ])

    person = users[chat_id]
    bot.sendMessage(chat_id, 'Current Category: ' + person.currentCategory +'\nBalance: '+ str(person.account.balance(person.currentCategory)) +'\n\nWhat can I do for you?', reply_markup=keyboard)










class Person:
	def __init__(self, userId, first_name):
		self.userId = userId
		self.first_name = first_name

		self.account= Account()

		self.makeNone()

	def makeNone(self):
	    self.currentCategory='NONE'
	    self.currentAction='NONE'



class Account:
	def __init__(self):
		self.entertainment=0
		self.personalCare=0
		self.foodAndDining=0
		self.autoAndTransport=0
		self.investmentAndDebtRepayment=0
		self.misc=0
		self.savings=0

		self.categories = {'Entertainment':self.entertainment,
							'Personal Care':self.personalCare,
							'Food and Dining':self.foodAndDining,
							'Auto and Transport':self.autoAndTransport,
							'Investments or Debt Repayments': self.investmentAndDebtRepayment,
							'Miscellaneous':self.misc,
							'Savings':self.savings
							}

	def update(self,category,amount):
		self.categories[category]+=float(amount)
		rounded= float("{0:.2f}".format(self.categories[category]))
		return rounded

	def reset(self,category):
		self.categories[category]=0

	def balance(self,category):
	    rounded= "{0:.2f}".format(self.categories[category])
	    return '$'+ (rounded)

	def spent_most_on(self):
	    list_of_values=self.categories.values()
	    amount=max(list_of_values)
	    string=''
	    max_categories=[]
	    for key,val in  self.categories.items():
	        if val==amount:
	            most=key
	            max_categories.append(key)
	            print(max_categories)
	    if len(max_categories)==1:
	        string= "You have spent the most on " +str(most)+ ",an amount of $"+ "{0:.2f}".format(amount)+'.\n'
	        return string
	    else:
	        tgt=''
	        for cat in max_categories:
	            tgt+= str(cat)+'\n'
	            string= "You have spent a maximum amount of $"+ "{0:.2f}".format(amount) +" in the following categories:\n" + tgt
	        return string

	def spent_least_on(self):
	    list_of_values=self.categories.values()
	    amount=min(list_of_values)
	    string=''
	    min_categories=[]
	    for key,val in  self.categories.items():
	        if val==amount:
	            least=key
	            min_categories.append(key)
	            print(min_categories)
	    if len(min_categories)==1:
	        string= "You have spent the least on " +str(least)+ ",an amount of $"+str(amount)+'.\n'
	        return string
	    else:
	        tgt=''
	        for cat in min_categories:
	            tgt+= str(cat)+'\n'
	        string= "You have spent a minimum amount of $"+ "{0:.2f}".format(amount) +" in the following categories:\n" + tgt
	        return string

	def total(self):
		list_of_values=self.categories.values()
		total_expenditure=0
		for val in list_of_values:
			total_expenditure+=val
		savings= self.categories['Savings']
		Net_expenditure= total_expenditure-savings
		string= "In total, you have spent $"+str(Net_expenditure)+ " and saved $"+str(savings)+"."
		return string

	def summary(self):
		#string=spent_most_on()+spent_least_on()
		#return string
		return self.total()+ "\n" + self.spent_most_on() + "\n" + self.spent_least_on()


	def reset_all(self):
		for key in self.categories.keys():
			self.categories[key]=0
		string='Data has been reset!'
		return string



















start_message = "Hello, I am Penny, your personal expenses manager. I will be keeping a record of your expenses. \nHow may I help you?"\

MessageLoop(bot, {'chat': on_chat_message,
				  'callback_query': on_callback_query}).run_as_thread()

print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
