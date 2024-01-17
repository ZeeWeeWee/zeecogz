import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import re
import json

class BdoNoticeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fetch_latest_notice(self, ctx):
        """
        Fetches the latest notice from the Black Desert Online website and stores the link in a JSON file.
        """
        url = 'https://www.naeu.playblackdesert.com/News/Notice/'
        data = self.fetch_and_parse(url)

        if isinstance(data, str) and "groupContentNo" in data:
            await ctx.send(f"Highest number data found: {data}")
            self.store_data(data)
            await ctx.send("Data stored.")
        else:
            await ctx.send(f"No valid data found or an error occurred: {data}")

    def fetch_and_parse(self, url):
        """
        Fetches and parses the specified URL to find the highest 'groupContentNo'.
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                thumb_nail_list = soup.find(class_='thumb_nail_list')
                hrefs = [li.find('a')['href'] for li in thumb_nail_list.find_all('li') if li.find('a')]

                highest_no = 0
                highest_no_data = None
                for href in hrefs:
                    match = re.search(r'groupContentNo=(\d+)', href)
                    if match:
                        content_no = int(match.group(1))
                        if content_no > highest_no:
                            highest_no = content_no
                            highest_no_data = href

                return highest_no_data or "No matching groupContentNo found."
            else:
                return f"Failed to fetch data. Status code: {response.status_code}"

        except requests.RequestException as e:
            return f"Error during requests: {str(e)}"

    def store_data(self, link, filename='data.json'):
        """
        Stores the provided link in a JSON file.
        """
        data = {"link": link}
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

    @commands.command()
    async def send_notice(self, ctx):
        """
        Sends the stored notice link to the Discord channel.
        """
        json_file = 'data.json'

        try:
            with open(json_file, 'r') as file:
                data = json.load(file)

            link = data.get('link')
            if link:
                await ctx.send(f"Here's your latest BDO notice: {link}")
            else:
                await ctx.send("No link found in the JSON file.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(BdoNoticeCog(bot))
