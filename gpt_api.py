from openai import OpenAI
import requests
import json
#import fact_check_api

#get key from file
with open(r'C:\Code\Python\Discord\fact_check_bot\openai_api_key.txt') as file:
    openai_api_key = file.read()

client = OpenAI(
  organization='org-o83g09q3iFh0JxM8BEJw35SA',
  project='proj_tFDFZoQE2SAyej3L2WtTLyku',
)

# Define the endpoint URL
url = "https://api.openai.com/v1/chat/completions"

# Define the headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

#returns a dict with truth verdict, explanation, and search tearms for fact check api
def analyze_disc_comment(comment):
    prompt ='''
            You are a highly accurate fact-checking bot tasked with verifying the truthfulness of statements.  



            When presented with a statement, your response should in valid JSON dictionary format of the following topics. 



            1. **Verdict:**
            - If the statement is **True**, start your response with "True."
            - If the statement is **False**, start your response with "False."
            - If the statement is **Not Making a Claim**, start your response with "Not Making a Claim."
            

            2. **Explanation:**
            - Provide a clear and concise explanation supporting your verdict.

            3. **Keywords that will be used to search google fact check:** 
            -Keywords must be concisely 2 or 3 words in the format 'word%20word%20word%20'
            -provide a tuple of 3 different sets of keywords to search
            -searching this database is very similar to searching google, choose the keywords accordingly.
       

            Example input:
            'They are eating the dogs in springfield ohio'

            Example output:

            {"Verdict" : "False","Explanation": "There have been no verified incidents or credible reports of dog consumption in Springfield, Ohio. Such claims are often exaggerated or unfounded.","Keywords": ["eating%20the%20{}dogs", "springfield%20{}ohio", "springfield%20{}dogs"]}

            #Note: If the comment is an oppinion, but is based off of a false statement, the verdict should be false. Or if the comment has *Notable Exceptions* or could be misconstrued to give someone the wrong idea the verdict should be false

            Here is the input:
            

'''
    
    # Define the data payload. This contains the prompt for the model
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": f"{prompt}\n{comment}"}],
        "temperature": 0.2
    }

    # Make the HTTP POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check the response
    if response.status_code == 200:
        #access the response
        arguments = response.json()["choices"][0]["message"]["content"]

        #gpt sometimes does not return valid json, if it fails to load, attempt 2 more times before returning None
        for _ in range(3):
            try:
                response_dict  = json.loads(arguments)
                return response_dict
            except:
                print('GPT response was not valid JSON, trying again...')
                pass
        
        #if it fails to load 3 times, return None
        return None




def create_fact_check_response(comment, verdict, explanation, links):

    prompt = f'''you are a highly accurate fact-checking bot tasked with verifying the truthfulness of statements. your specific function is to understand the comment, verdict, explanation, and then choose from a list of links that best refutes or confirms the comment based on the verdict.
     your response should be in understandable enlgish. It should be fairly concise as the response will be a comment in a discord political channel. People should see your responses as highly accurate, neat and helful political fact check.
     Example response:
        "The claim (a brief summary of the claim) is misleading (or other word to fittingly descriptive word to describe its truthyness).\n\n There have been no verified incidents or credible reports of dog consumption in Springfield, Ohio. Such claims are often exaggerated or unfounded. \n\nhttps://www.newsweek.com/donald-trump-cats-dogs-claim-debate-video-fact-check-election-2024-1952779"

    comment: {comment}
    verdict: {verdict}
    explanation: {explanation}
    links: {links}  

    Note: If the link does not appear to directly refute the arugment, you should not include it and perhaps mention you couldnt find the exact link, but encourage people to consider fact checking the argument
'''
    # Define the data payload. This contains the prompt for the model
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": f"{prompt}\n\n{comment}"}],
        "temperature": 0.1
    }

    # Make the HTTP POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check the response
    if response.status_code == 200:
        #access the response
        response = response.json()["choices"][0]["message"]["content"]

        return response
    else:
        return None













def get_arguemnt_keywords(comment):

    prompt = ''''You are a fact-checking bot. Return a Python dictionary where each key is a complete restatement of the argument, presented in full context and detail. Values should be concisely 3 words each (absolutely no less and no more) and include multiple distillations for each key, so use a list. The goal is to use these keywords for database searching, much like a google search. The first k,v in the dict should indicate if a political argument was presented (not an analogy or other conversational words. i.e. "political_argument":"Yes"). If it is false, only respond with {"political_argument": "No"} (this requires nuance. Use your most current understanding to recognize hot political topics. Even if the comment doesnt seem to present a structured political argument, if it is based in a political misunderstanding, then you should return Yes for this) The response must be returned in valid JSON format without any extra characters such as code fences, backticks, or indentation. Ensure the response is consistently structured and always adheres to the proper JSON format. Here an example of how every response should look {'political_argument': True, 'A full and detailed summery of arguemnt 1' : ['2-3_keywords', '2-3_keywords', '2-3_keywords'], 'A full and detailed summery of arguemnt 2' : ['2-3_keywords', '2-3_keywords', '2-3_keywords']}'''

    # Define the data payload. This contains the prompt for the model
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": f"{prompt}\n\n{comment}"}],
        "temperature": 0.1
    }

    # Make the HTTP POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check the response
    if response.status_code == 200:
        #access the response
        arguments = response.json()["choices"][0]["message"]["content"]

        try:
            #gpt returns a json object but its a string, turn it into a dictionary
            argument_dict = json.loads(arguments)
            
            #since we don't know the keys or values, transform the dictionary into a list of tuples
            political_arguments = list(argument_dict.items())
        except:
            #if the response is not a valid json, return a dictionary with the political argument key set to no for convenience
            argument_dict = {"political_argument": "No", "error": "invalid json"}

        if political_arguments[0][1] == "Yes":
            
            return political_arguments
        else:
            print(f"No political argument was found:\n{comment}")
            return None
            
    
    else:
        print(f"Error: {response.status_code}")

def analyze_fact_check_response(fact_check_response):

    prompt = f"""
you are a function within a bot that is designed to fact checkpolitical arguments made in discord. Your role will be to receive a tuples of fact checking data, You will decide if there is a match and determine the best match if there are multiples, and return a valid JSON object with the following keys: Title, Link, Truth_Rating, Explanation.

   
This is how the tuple is structured:
('Claim', 'Keywords', 'Title', 'Link', 'Truth_Rating')
you must first understand the claim, which is the argument made by the discord user, then look at title, link and truth rating to determine if the claim is being refuted. If you find successful refutations, you must determine which refute does so the best, then return that tuple in a JSON object. Once the best tuple has been selected, read the article and quote the part that directly refutes the arugment.


**Example Input:**

[
    ('They are eating the dogs in Springfield, Ohio.', 'Springfield%20Ohio', 'Immigrants are not eating the dogs in Springfield, Ohio', 'https://www.usatoday.com/story/news/factcheck/2024/09/20/eating_dog_fact_check/75304414007/', 'False'),
    ('They are eating the dogs in Springfield, Ohio.', 'Springfield%20Ohio','Photo Does Not Show RFK Jr. Eating Dog — or Goat', 'https://www.snopes.com/fact-check/rfk-dog-photo/'
]



**Example Output:**
{{
  "Title": "Immigrants are not eating the dogs in Springfield, Ohio",
  "Link": "https://www.usatoday.com/story/news/factcheck/2024/09/20/eating_dog_fact_check/75304414007/",
  "Truth_Rating": "False",
  "Quoted_Refutation": "City leaders say the immigrants are welcome and integral parts of the community, and USA TODAY and other outlets have debunked the claim of pet eating."
}}



Remember:
the refute must actually refute the claim, and humans should be able to make the logical connection. 
Sometimes an you will not find an article that refutes the claim. In this event, return nothing for that tuple. It is vastly better to reurn nothing than incorrect information.
Valid JSON is required for the response. do not use any extra ticks or anything special, your response will be processed by the JSON library and must be valid.

Here is the list:
{fact_check_response}

"""
    # Define the data payload. This contains the prompt for the model
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }

    # Make the HTTP POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check the response
    if response.status_code == 200:
        # Access the response
        arguments = response.json()["choices"][0]["message"]["content"]

        try:
            # GPT returns a JSON object but it's a string, turn it into a dictionary
            argument_dict = json.loads(arguments)
            
            # Since we don't know the keys or values, transform the dictionary into a list of tuples
            analyzed_fact_check = list(argument_dict.items())
        except:
            # If the response is not valid JSON, return a dictionary with an error message
            argument_dict = {"error": "Invalid JSON"}
            analyzed_fact_check = list(argument_dict.items())

        return analyzed_fact_check
    else:
        # Handle the case where the response is not successful
        return {"error": f"Request failed with status code {response.status_code}"}
