from phd_bot import PhdBot
import datetime

def compile_send():
    result = PhdBot()
    list_opportunities = result.generate_opportunities('autonomous')
    html_content = result.convert_opportunities_to_html(list_opportunities)
    result.send_email('adegokesimi@gmail.com', 'Phd Opportunities '+ datetime.datetime.utcnow().ctime(), html_content)
    
if __name__ == "__main__":
    compile_send()