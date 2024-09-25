import gpt_api
import requests
import os
import json
import random




#returns a list of tuples like so
# [(title, link, news_agency_truth_rating)]


def get_fact_check_response(keywords):

    fact_check_links = []

    for keyword_search in keywords:

        url = f'https://toolbox.google.com/factcheck/api/search?hl=en&num_results=20&force=false&offset=0&query={keyword_search}'

        #send request to google fact check api. It will return a .bin file
        response = requests.get(url)



        # Check if the response status is OK
        if response.status_code == 200:

            #attempt to remove old file if it exists
            try:
                os.remove('response.bin')
            except FileNotFoundError:
                pass

            #in python we can choose the name when we file.write(response.content)
            with open("response.bin", "wb") as file:
                file.write(response.content)

            # read the file
            with open("response.bin", "r", encoding="utf-8") as file:
                content = file.read()



            # Once we're done processing, delete the file
            os.remove("response.bin")

            #remove the random extra characters at the beginning of the file, then parse
            cleaned_content = content[6:]
            parsed_content = json.loads(cleaned_content)

            counter = 0

            #print(f'parsed_content: {parsed_content}\n\n')

            try:
                for i in parsed_content[0][1]:
                    
                    #counter logic  
                    counter += 1
                    if counter > 5:
                        counter = 0
                        break

                    link = i[0][3][0][1]
                    fact_check_links.append(link)
            except:
                pass
    return fact_check_links















#note to self: if there are multilple political arguemnts, let fact_check_main handle the itteration logic
def get_fact_check_response_old(political_argument):

    #extract the keyword list from the response
    keywords = political_argument[1]


    if isinstance(keywords, str):
        try:
            #this is actually a string, so format it for jason then convert it to a list
            json_string = keywords.replace("'", '"') #this crashed once
            keywords = json.loads(json_string)
        except:
            print(f'Error inside fact_check_api.get_fact_check_response():  Could not convert the keywords to a list.\n\n{keywords}\n\n')

    #initialize list to hold the encoded keywords
    encoded_keywords = []

    # Iterate through the list and replace spaces with %20
    for keyword in keywords:
        encoded_keywords.append(keyword.replace(' ', '%20'))

    #initialize list to hold the parsed content
    #list items will be tuples like so [(title, link, news_agency_truth_rating)]
    fact_check_response = []

    for keywords in encoded_keywords:

        #cache bust makes sure we get a new response every time. If the website used our cache it would change the structure of the response
        random_param = random.randint(0, 100000)
        url = f'https://toolbox.google.com/factcheck/api/search?hl=en&num_results=20&force=false&offset=0&query={keywords}&cache_bust={random_param}'




        #send request to google fact check api. It will return a .bin file
        response = requests.get(url)



        # Check if the response status is OK
        if response.status_code == 200:

            #attempt to remove old file if it exists
            try:
                os.remove('response.bin')
            except FileNotFoundError:
                pass

            #in python we can choose the name when we file.write(response.content)
            with open("response.bin", "wb") as file:
                file.write(response.content)

            # read the file
            with open("response.bin", "r", encoding="utf-8") as file:
                content = file.read()



            # Once we're done processing, delete the file
            os.remove("response.bin")

            #remove the random extra characters at the beginning of the file
            cleaned_content = content[6:]

            #parse the json
            parsed_content = json.loads(cleaned_content)

            #json.loads might return None if the json is invalid. if it does, dont attempt to parse it
            if isinstance(parsed_content, list) and parsed_content is not None:
                try:
                    #remove the first element in the list
                    parsed_content = parsed_content[0][1]
                except IndexError:
                    print(f'Error inside fact_check_api.get_fact_check_response():  Bad resopnse from google fact check api. Ignoring this keyword: {keywords}\n')
                    continue
                
                #only collect the first 3 results
                counter = 0
                if isinstance(parsed_content, list) and parsed_content is not None:

                    for i in parsed_content:
                

                        #counter logic  
                        counter += 1
                        if counter > 3:
                            counter = 0
                            break

                        #print(f'counter: {counter}')


                        political_claim = political_argument[0]

                        #extract the title, link, and accuracy
                        title = i[0][0]
                        link = i[0][3][0][1]
                        news_agency_truth_rating = i[0][3][0][3]

                        #print(f'Claim: {political_claim}\nTitle: {title}\nLink: {link}\nNews Agency Truth Rating: {news_agency_truth_rating}\n\n')  
                        fact_check_response.append((political_claim, keywords, title, link, news_agency_truth_rating))



    else:
        print(f"Error: Received response with status code {response.status_code}. Ignoring this keyword: {keyword}\n")
    return fact_check_response

testing = 0

if testing == 1:
    response = gpt_api.get_arguemnt_keywords('''I can't believe the government is secretly controlling the weather using chemtrails. Just last week, it started raining green-colored water in our city! This proves that they're manipulating the climate to enforce their agenda.''')
    print(type(response))
    print(response)


    #response = [('political_argument', 'Yes'), ("Vaccines are part of a global depopulation plan orchestrated by world elites. The microchips in vaccines are tracking our every move, and the side effects are causing long-term health issues that they're hiding from the public.", ['vaccine conspiracy theory', 'global depopulation plan', 'tracking microchips health issues'])]

    fact_check = get_fact_check_response(response)

    for i in fact_check:
        print(f'claim: {i[0]}\nkeywords: {i[1]}\n\nTitle: {i[2]}\nLink: {i[3]}\nNews Agency Truth Rating: {i[4]}\n\n')