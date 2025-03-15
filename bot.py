from rubpy import Client, filters, utils
from rubpy.types import Updates 
from bs4 import BeautifulSoup
import requests
import re
import socket
from urllib.parse import urlparse



# تابعی برای تشخیص تکنولوژی‌ها و آی‌پی سایت
def analyze_website(url):
    try:
       
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

       
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"error": "Unable to reach the website."}

    
        domain = urlparse(url).hostname
        ip_address = socket.gethostbyname(domain)

        # تجزیه و تحلیل HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        technologies = set()

        # بررسی اسکریپت‌ها
        for script in soup.find_all('script', src=True):
            src = script['src'].lower()
            if 'react' in src:
                technologies.add('React')
            elif 'angular' in src:
                technologies.add('Angular')
            elif 'vue' in src:
                technologies.add('Vue.js')
            elif 'jquery' in src:
                technologies.add('jQuery')
            elif 'bootstrap' in src:
                technologies.add('Bootstrap')
            elif 'node_modules' in src:
                technologies.add('Node.js')
            elif 'requirejs' in src:
                technologies.add('RequireJS')
            elif 'ajax.googleapis.com' in src:
                technologies.add('Google Hosted Libraries')

      
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '').lower()
            if 'bootstrap' in href:
                technologies.add('Bootstrap')
            elif 'wp-content' in href:
                technologies.add('WordPress')
            elif 'joomla' in href:
                technologies.add('Joomla')

      
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            technologies.add(generator['content'])

        # بررسی محتوای HTML برای CMS
        content = response.text.lower()
        if 'wp-content' in content:
            technologies.add('WordPress')
        if 'joomla' in content:
            technologies.add('Joomla')
        if 'drupal' in content:
            technologies.add('Drupal')

        # افزودن HTML/CSS/JS به عنوان تکنولوژی پایه
        if any(tag in content for tag in ('html', 'css', 'javascript')):
            technologies.add('HTML/CSS/JavaScript')

        return {
            "ip_address": ip_address,
            "technologies": sorted(technologies),
            "status": "success"
        }

    except requests.exceptions.Timeout:
        return {"error": "Request timed out."}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {str(e)}"}
    except socket.gaierror:
        return {"error": "Could not resolve the domain to an IP address."}

app = Client(" analyze_website")

@app.on_message_updates(filters.is_private)
async def handle_message(event: Updates ):
    if event.text and (event.text.startswith("http://") or event.text.startswith("https://")):
        result = analyze_website(event.text)
        if result.get("status") == "success":
            message = (
                "🌐 **Website Analysis** 🌐\n\n"
                f"🔗 **URL:** {event.text}\n"
                f"📡 **IP Address:** {result['ip_address']}\n"
                f"🛠️ **Technologies:**\n"
                + "\n".join(f"  - {tech}" for tech in result['technologies'])
            )
        else:
            message = f"❌ **Error:** {result.get('error', 'Unknown error occurred.')}"
        await event.reply(message)
    else:
        await event.reply("🔍 Please send a valid URL starting with http:// or https://")

app.run()
