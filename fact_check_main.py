import discord_bot
import gpt_api
import fact_check_api
import os



'''
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW

This is deprecated dont use

WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
'''

#run the bot
#discord_bot.main()


response = gpt_api.analyze_disc_comment(comment)

print(response)

if response != None:

    if response['Verdict'] == 'False':

        fact_check_links = fact_check_api.get_fact_check_response(response['Keywords'])


        if len(fact_check_links) == 0:
            fact_check_links = None
        fact_check_response = gpt_api.create_fact_check_response(comment, response['Verdict'], response['Explanation'], fact_check_links)

        os.system('cls')

        return (fact_check_response)












problematic_comments =['Solar energy production surpassed fossil fuels in 2020.']













'''
gpt_response  = gpt_api.get_arguemnt_keywords("They are eating the dogs in springfield ohio")

if gpt_response is not None:
    #check if comment was making a political argument
    if gpt_response[0][1] == 'Yes':
        gpt_response = gpt_response[1:]

    potential_fact_checks = []

    for i in gpt_response:
        fact_check_response = fact_check_api.get_fact_check_response(i)
        potential_fact_checks.append(fact_check_response)


    #print(f'potential_fact_checks: {potential_fact_checks}\n\n')

    for i in potential_fact_checks:
        response = gpt_api.analyze_fact_check_response(i)

        print(f'fact check tuple: {i}\n\n')
        print(f'fact_check_response: {response}\n\n')

    #for i in political_argument:
        #print(f'claim: {i[0]}\nkeywords: {i[1]}\n\nTitle: {i[2]}\nLink: {i[3]}\nNews Agency Truth Rating: {i[4]}\n\n')
        
    #print(political_argument)
'''