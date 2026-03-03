import random
import requests
import time
last_request = 0.0
def safe_get(url:str,
             *,
             headers:dict|None=None,
             attempts:int=3,
             min_interval:float=0.5,
             time_out:tuple[float,float]=(3,10)#(for connect and read(if the connection to the api failed -->raise error after 3s and if nno data retreived also raise error after 10s))
             )-> requests.Response :
    
    '''
    -get statemnet 
    -wait for the errors of "so many requests"
    -emerge the funciton rate_limit for the big pic (not bypass the number if requests allowed in minuit)
    -except statemnt for the request.exeption 
    -rais error for the 4xx and 5xx errors and deal with it in the except function 
    -variable for the last error for anlyze after finish the process 
    '''
    Retry_After = None
    wait = None
    last_error :Exception |None = None
    
    for attempt in range(attempts):
        try :
            rate_limit(min_interval)
            resp = requests.get(url=url,headers=headers,stream=True,timeout=time_out)
            if resp.status_code == 429 :
               Retry_After = resp.headers.get("Retry-After")
               if Retry_After and Retry_After.isdigit():
                   wait  = int(Retry_After) +random.uniform(0,1)
               else :
                   wait = 2**attempt + random.uniform(0,1)
               time.sleep(wait)
               continue
            if 500<= resp.status_code <=599:
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
                continue
            if 400<= resp.status_code <=499:
                resp.raise_for_status()
            #the other cases is to success
            return resp
            
        except (requests.exceptions.Timeout ,requests.exceptions.ConnectionError) as e  :
            last_error = e 
            if attempt < attempts-1 :
                wait = 2**attempt + random.uniform(0,1)
                time.sleep(wait)

            else :
                break
        except requests.exceptions.RequestException as e :
            last_error = e 
            if attempt < attempts-1 :
                wait = 2**attempt + random.uniform(0,1)
                time.sleep(wait)

            else :
                break
        except requests.exceptions.HTTPError as e :
            last_error = e 
            raise
    raise RuntimeError(f"attepts failed due to {e} error numbers of attempts are {attempts}")



def rate_limit(mini_intervall:float=0.5):
    global last_request
    now = time.time()
    diff = now - last_request

    if diff <mini_intervall :
        time.sleep(mini_intervall-diff)
    last_request = time.time()

headers = {"User-Agent": "Mozilla/5.0" }
r = safe_get("https://upload.wikimedia.org/wikipedia/commons/3/3f/Fronalpstock_big.jpg", headers=headers)
with open("file__.jpg","wb") as f :
    for chunk in r.iter_content(8192) :
        if chunk :
            f.write(chunk)
    
    print('done')
        