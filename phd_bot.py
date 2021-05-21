import requests
from bs4 import BeautifulSoup
from phd_opportunity import PhDOpportunity
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
from dotenv import load_dotenv
load_dotenv()

class PhdBot:
    def __init__(self) -> None:
        pass
    
    def generate_opportunities(self, keyword, pageNumber=1):
        self.findphd_url = 'https://www.findaphd.com/phds/non-eu-students/?01w0&Keywords={}&PG={}'
        self.keyword_param = keyword
        self.pagenumber_param = pageNumber

        self.url = self.findphd_url.format(self.keyword_param, pageNumber)
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

        req = requests.get(self.url, headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        
        result_class = 'resultsRow'
        mydivs = soup.find_all("div", class_=result_class)
        
        opportunities = []

        for divs in mydivs:
            if divs is not None:
                title = divs.find('h3').get_text() if divs.find('h3') is not None else ''
                university = divs.find('div', class_='instDeptRow').get_text().strip().replace("\n\n", ", ") if divs.find('div', class_='instDeptRow') is not None else ''
                description = divs.find('div', class_='descFrag').get_text().strip().replace("Read more", "") if divs.find('div', class_='descFrag') is not None else ''
                read_more = divs.find('a', class_='phd-result__description--read-more').get('href') if divs.find('a', class_='phd-result__description--read-more') is not None else ''
                url_link = 'https://www.findaphd.com'+read_more
                
                if len(title) != 0:
                    opportunity = PhDOpportunity(title, university, description, url_link)
                    opportunities.append(opportunity)
                
        
        return opportunities
    
    def convert_opportunities_to_html(self, opportunities):
        
        html_content = ''
        for obj in opportunities:
            content =  '''<div style="line-height:28px;font-family: Arial Regular, sans-serif; font-size: 16px; letter-spacing:.8px; color: #605f5d;">

                                            <h3>{}</h3>
                                            <h4>{}</h4>
                                            <p> {}</p>
                                            <a href="{}">Read more</a>
                                        </div>'''
            obj_content = content.format(obj.title, obj.university, obj.description, obj.link)
            html_content+= obj_content
            
        body = html_content.replace("\n", "").replace("(\'", "").replace("\',)", "")
            
        with open('index.html') as f:
            email_contents = f.read()
            
        email_body = email_contents.replace('email_to_replace', body).replace("\n", "")
            
        
        return email_body
    
    def send_email(self, receiver_email, subject, email_body):
        receiver_email = receiver_email
        sender_email  = 'tobymathy3@gmail.com'
        password = os.environ.get('password') #this is not secure

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        # Create the plain-text and HTML version of your message
        html = email_body

        # Turn these into plain/html MIMEText objects
        part2 = MIMEText(html, "html")

        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )