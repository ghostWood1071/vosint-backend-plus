import json
import time
import random
time_waiting = random.randint(1,7)


from playwright.sync_api import sync_playwright
def fb_page(browser,link_cookies='/home/ds1/vosint/v-osint-backend/vosint_ingestion/facebook/cookies.json',link_person = ''):
    data = {}
#with sync_playwright()as p:
    # Launch a new browser instance
    #browser = p.chromium.launch()

    # Create a new browser context and page
    context = browser.new_context()
    page = context.new_page()

    # Load cookies from file
    with open(link_cookies, 'r') as f:
        cookies = json.load(f)

    # Add cookies to the browser context
    context.add_cookies(cookies)

    # Navigate to a page that requires authentication
    #page = context.new_page()

    # Navigate to the login page
    page.goto(link_person)
    time.sleep(time_waiting)
    #page.goto("https://mbasic.facebook.com/groups/zui.vn")

    page.keyboard.press('End')
    page.wait_for_selector('body')
    time.sleep(2)

    # # Fill in the login form
    # # page.fill("#m_login_email", "don.chicharito@gmail.com")
    by = "css="
    # expr = "#m_login_email"
    # from_element = page.locator(f"{by}{expr}")
    # from_element.type("don.chicharito@gmail.com")

    # expr = 'input[type="password"]'
    # from_element = page.locator(f"{by}{expr}")
    # from_element.type("vjetanh8h")
    def select(from_element, expr, by = "css="):
        element = from_element.locator(f"{by}{expr}")
        element = [element.nth(i) for i in range(element.count())]
        return element
    person = select(page,"article")
    #person = select(person[0],"article")
    datas = []
    for i in range(len(person)):
        data = {}
        data['id'] = link_person.replace('https://','').replace('mbasic.facebook.com/','').replace('?v=timeline','')
        data["id_data_ft"] = person[i].get_attribute('data-ft')
        try:
            abc = select(person[i],'header')
            #print('header',abc[0].inner_text())
            data['header'] = abc[0].inner_text()
        except:
            pass
        
        try:
            abc = select(person[i],'div[data-ft=\'{"tn":"*s"}\']')
            #print('content',abc[0].inner_text())
            data['content'] = abc[0].inner_text()
        except:
            pass

        try:
            abc = select(person[i],'abbr')
            #print('date',abc[0].inner_text())
            date = abc[0].inner_text()
            
            abc = select(person[i],'footer div abbr')
            # print('footer_date',abc[0].inner_text())
            data['footer_date'] = abc[0].inner_text()
        except:
            pass
        
        try:
            # abc = select(person[i],'footer div')
            # footer_type =abc[1].inner_text()
            # print("footer_type",footer_type)
            data['footer_type'] = 'page'#footer_type
        except:
            pass
        
        try:
            abc = select(person[i],'footer div')
            footer_str =abc[2].inner_text()
            
            tmp = footer_str.split(" ")
            #print(tmp)
        
            for j in range(2,len(tmp)):
                if tmp[j] == "Like":
                    try:
                        sl = int(tmp[j-1])
                        data['like']=sl
                    except:
                        try:
                            sl = int(tmp[j-2])
                            data['like']=sl
                        except:
                            pass
                elif tmp[j] == "Comments":
                    try:
                        sl = int(tmp[j-1])
                        data['comments']=sl
                    except:
                        pass
                elif tmp[j] == "Share":
                    try:
                        sl = int(tmp[j-1])
                        data['share']=sl
                    except:
                        pass
            #print(data)
        except:
            pass
        
        # comment = select(person[i],'.nowrap')
        # comment[0].click()
        # time.sleep(2)

        # try:
        #     abc = select(page,'div[data-ft=\'{"tn":"*s"}\']')
        #     #print('content',abc[0].inner_text())
        #     data['content'] = abc[0].inner_text()
        # except:
        #     pass

        # #abc = select(page,'#m_story_permalink_view')
        # abc = select(page,'.dh')
        # # print(abc[0].inner_text())
        # comments_content = []
        # for k in abc:
        #     tmp={}
        #     header = select(k,'a.di.bf')
        #     # print(header)
        #     tmp['header_href'] = header[0].get_attribute('href')
        #     tmp['herder']= header[0].inner_text()
        #     tmp['content']= select(k,'div.dj')[0].inner_text()
        #     comments_content.append(tmp)
        # data['comments_content'] = comments_content

        # try:


        #     comment = select(person[i],'.nowrap')
        #     comment[0].click()
        #     time.sleep(2)

        #     try:
        #         abc = select(page,'div[data-ft=\'{"tn":"*s"}\']')
        #         #print('content',abc[0].inner_text())
        #         data['content'] = abc[0].inner_text()
        #     except:
        #         pass

        #     abc = select(page,'#m_story_permalink_view')
        #     abc = select(abc[0],'.dh')
        #     # print(abc[0].inner_text())
        #     comments_content = []
        #     for k in abc:
                
        #         tmp={}
        #         header = select(k,'a.di.bf')
        #         # print(header[0].inner_text())
        #         tmp['header_href'] = header[0].get_attribute('href')
        #         tmp['herder']= header[0].inner_text()
        #         tmp['content']= select(k,'div.dj')[0].inner_text()
        #         comments_content.append(tmp)
        #     data['comments_content'] = comments_content
        # except:
        #     pass
        # finally:
        #     page.goto(link_person)
        #     #page.goto("https://mbasic.facebook.com/groups/zui.vn")

        #     page.keyboard.press('End')
        #     page.wait_for_selector('body')
        #     time.sleep(1)
        
        datas.append(data)
    #print(datas)
    return datas

#fb_groups(link_person="https://mbasic.facebook.com/thanh.bi.73")     
