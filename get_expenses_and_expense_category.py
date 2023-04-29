
import json

from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    expenses:str

class exp(BaseModel) :
    monthly_income: str
    monthly_expense_food: str
    monthly_expense_rent: str
    monthly_expense_education: str
    monthly_expense_transportation: str
    monthly_expense_insurance: str
    monthly_expense_other: str
    monthly_saving_target: str

class final(BaseModel):
    user_expense:User
    expense_category: exp

data = [{'name': "Bob", 'monthly_income': '2500.0', 'monthly_expense_food': '300.0', 'monthly_expense_rent': '1000.0', 'monthly_expense_education': '800.0', 'monthly_expense_transportation': '100.0', 'monthly_expense_insurance': '100.0', 'monthly_expense_other': '200.0', 'monthly_saving_target': '150.0', 'expenses': '2500.0'}, {'name': "Anna", 'monthly_income': '5000.0', 'monthly_expense_food': '300.0', 'monthly_expense_rent': '2000.0', 'monthly_expense_education': '0.0', 'monthly_expense_transportation': '100.0', 'monthly_expense_insurance': '200.0', 'monthly_expense_other': '500.0', 'monthly_saving_target': '400.0', 'expenses': '3100.0'}, {'name': "Jen", 'monthly_income': '12000.0', 'monthly_expense_food': '800.0', 'monthly_expense_rent': '4500.0', 'monthly_expense_education': '0.0', 'monthly_expense_transportation': '300.0', 'monthly_expense_insurance': '700.0', 'monthly_expense_other': '800.0', 'monthly_saving_target': '1000.0', 'expenses': '7100.0'}]


def get_user_and_expense(usr_1):
    data1 = json.dumps(data)
    data2 = json.loads(data1)

    data_needed = {}
    user_expenses = {}
    expenses_category = {}

    for i in data2:
        if i['name'] == usr_1:
            data_needed['name']= i['name'] ,
            data_needed['expenses'] =  i['expenses'],
            data_needed['monthly_income']  =   i['monthly_income'],
            data_needed['monthly_expense_food'] = i['monthly_expense_food'],
            data_needed['monthly_expense_rent'] = i ['monthly_expense_rent'],
            data_needed['monthly_expense_education']   = i['monthly_expense_education'],
            data_needed['monthly_expense_transportation']=  i['monthly_expense_transportation'],
            data_needed['monthly_expense_insurance'] = i ['monthly_expense_insurance'],
            data_needed['monthly_expense_other'] =i['monthly_expense_other'],
            data_needed['monthly_saving_target'] = i['monthly_saving_target']

            user_expenses['name'] = str(data_needed['name'] )
            user_expenses['expenses'] =   str(data_needed['expenses'] )


            expenses_category['monthly_income'] = str(data_needed['monthly_income'])
            expenses_category['monthly_expense_food'] =   str(data_needed['monthly_expense_food'])
            expenses_category['monthly_expense_rent'] = str(data_needed['monthly_expense_rent'])
            expenses_category['monthly_expense_education'] = str(data_needed['monthly_expense_education'])
            expenses_category['monthly_expense_transportation'] =str(data_needed['monthly_expense_transportation'])
            expenses_category['monthly_expense_insurance'] = str(data_needed['monthly_expense_insurance'] )
            expenses_category['monthly_expense_other'] =str(data_needed['monthly_expense_other'])
            expenses_category['monthly_saving_target'] = str(data_needed['monthly_saving_target'] )


            m = final(
              user_expense = user_expenses,
                expense_category = expenses_category)

            m1 = m.json().replace('"(','').replace(')"','') .replace(',,',',')
            return m1

# usr = 'Anna'
# k = get_user_and_expense(usr)
