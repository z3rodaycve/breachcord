# If you are using Git to track your bot's changes, you should create a file called .gitignore and add .env to it. This stops your .env file from getting tracked along with the rest of your code, and will not be pushed to a remote Git repository. As a consequence, it will stay secure on your local machine.
import discord

import datetime
import time
import asyncio
from io import BytesIO
import json
import os
from dotenv import load_dotenv

import handler # Data Breach Lookup Handler (intelx, hibp)

# Console Colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# User-Search Data
load_dotenv()
search_data = {}

bot = discord.Bot(intents=discord.Intents.all())
bot_name = os.getenv('BOT_NAME')
bot_photo = os.getenv('BOT_ICON')

# Discord.py Views

# ============================
#           IntelX
# ============================
class intelx_results(discord.ui.View):
    def __init__(self, records, domain, author_id, page_size=1):
        super().__init__(timeout=None)
        self.records = records
        self.domain = domain
        self.author_id = author_id
        self.page_size = page_size
        self.current_page = 0
        self.total_pages = max(1, (len(self.records) + page_size - 1) // page_size)
        self.update_label()

    @discord.ui.button(label="Download results (JSON)", style=discord.ButtonStyle.secondary, emoji="📦", custom_id="download_results")
    async def download_results(self, button: discord.ui.Button, interaction: discord.Interaction):
        time_now = datetime.datetime.now(datetime.UTC)

        if interaction.user.id != self.author_id: # discord userid check
            incorrect_embed = discord.Embed(title="❌  Restricted Access", description=f"You cannot download someone else's search results.", color=discord.Color.darkred())
            incorrect_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            await interaction.response.send_message(embed=incorrect_embed, ephemeral=True)
            return

        results_file = BytesIO(json.dumps({"records": self.records}, indent=4).encode("utf-8"))
        file = discord.File(results_file, filename=f"results[{self.domain}].json")

        results_embed = discord.Embed(title="📦  Search Results", description=f"Here are your search results in the JSON format (.json)", color=discord.Color.gold())
        results_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        results_embed.set_footer(text="Below you can see the results file in json.")

        await interaction.response.send_message(embed=results_embed, ephemeral=True)
        await interaction.followup.send(file=file, ephemeral=True)

        print(f"{bcolors.WARNING}[SEARCH DOWNLOAD]{bcolors.ENDC} Search results downloaded | Discord User-ID: {self.author_id} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary, custom_id="previous_page")
    async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author_id: # discord userid check
            incorrect_embed = discord.Embed(title="❌  Restricted Access", description=f"You cannot control someone else's pagination.", color=discord.Color.darkred())
            incorrect_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            await interaction.response.send_message(embed=incorrect_embed, ephemeral=True)
            return

        if self.current_page > 0:
            self.current_page -= 1
        embed = self.update_embed(self.current_page)
        self.update_label()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="1/1", style=discord.ButtonStyle.gray, disabled=True, custom_id="page_number")
    async def page_display(self, button: discord.ui.Button, interaction: discord.Interaction):
        navigation_embed = discord.Embed(title="❔  Navigation", description=f"Use the arrows to navigate.", color=discord.Color.lightgrey())
        navigation_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        await interaction.response.send_message(embed=navigation_embed, ephemeral=True)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary, custom_id="next_page")
    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.author_id: # discord userid check
            incorrect_embed = discord.Embed(title="❌  Restricted Access", description=f"You cannot control someone else's pagination.", color=discord.Color.darkred())
            incorrect_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            await interaction.response.send_message(embed=incorrect_embed, ephemeral=True)
            return

        if self.current_page < max(0, self.total_pages - 1):
            self.current_page += 1
        embed = self.update_embed(self.current_page)
        self.update_label()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_label(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.custom_id == "page_number":
                item.label = f"{self.current_page+1}/{self.total_pages}"
                break

    def update_embed(self, index: int):
        index = max(0, min(index, self.total_pages - 1))
        start_index = index * self.page_size
        end_index = start_index + self.page_size
        update_records = self.records[start_index:end_index]
        embed = discord.Embed(title=f"🗃️ Page {index+1} of search ({self.domain})", description="", color=discord.Color.dark_theme())
        
        if not update_records:
            embed.add_field(name="No results on this page", value="", inline=False)
        else:
            for record in update_records:
                intelx_systemid = record.get("systemid","")
                publication_date = record.get("date", record.get("added",""))
                leak_name = record.get("name","")
                leak_group = record.get("bucketh", record.get("group",""))

                embed.add_field(name="IntelX System-ID:", value=f"*{intelx_systemid}*", inline=False)
                embed.add_field(name="IntelX Link:", value=f"*[See results on IntelX](https://intelx.io/?s={intelx_systemid})*", inline=False)
                embed.add_field(name="Publication date:", value=f"*{publication_date}*", inline=False)
                embed.add_field(name="Leak name:", value=f"*{leak_name}*", inline=False)
                embed.add_field(name="Leak group:", value=f"*{leak_group}*", inline=False)

        embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        embed.set_footer(text=f"Page {index+1} of {self.total_pages}   •   Total results: {len(self.records)}")
        return embed
class intelx_search(discord.ui.View): 
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Search", style=discord.ButtonStyle.primary, emoji="🔍", custom_id="search")
    async def search_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        data = search_data.get(self.user_id, {})
        results_amount = data.get("results_amount", "n/a")
        query = data.get("query", "n/a")
        time_now = datetime.datetime.now(datetime.UTC)

        print(f"{bcolors.OKCYAN}[INTELX SEARCH START]{bcolors.ENDC} Discord User-ID: {self.user_id}, Search Query: {query}, Requested Results: {str(results_amount)} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
        

        started_embed = discord.Embed(title="🕓  Search Query Started", description="A search query has started.", color=discord.Color.blurple())
        started_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        started_embed.set_footer(text=f"Search started by {self.user_id} on {time_now.strftime("%c")}(UTC)")

        await interaction.response.send_message(embed=started_embed)

        results_data = await asyncio.to_thread(handler.intelx_search, query, results_amount)

        if results_data.get("status", 0) == 1 or results_data.get("status", 0) == 3:
            ts_start = results_data.get("timestamp_start", 0)
            ts_end = results_data.get("timestamp_end", time.time())

            summary_embed = discord.Embed(title="❌  No results", description=f"A search has returned total of 0 results.", color=discord.Color.dark_red())
            summary_embed.add_field(name="📂 Total results:", value=f"*0*", inline=False)
            summary_embed.add_field(name="🔑 Query keyword:", value=f"*{query}*", inline=False)
            summary_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            summary_embed.set_footer(text=f"No results found for the query   •   Time passed: {ts_end - ts_start:.2f}s")
            
            await interaction.followup.send(embed=summary_embed)
        elif results_data.get("status", 0) == 2:
            print(f"{bcolors.FAIL}[SEARCH MALFUNCTION]{bcolors.ENDC} Error: Search ID not found | Discord User-ID: {self.user_id}, Search Query: {query}, Requested Results: {str(results_amount)} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

            ts_start = results_data.get("timestamp_start", 0)
            ts_end = results_data.get("timestamp_end", time.time())
            
            summary_embed = discord.Embed(title="❌  Search Error", description=f"Your search has stumbled on a problem while trying to run. Try again or see logs.", color=discord.Color.dark_red())
            summary_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            summary_embed.set_footer(text=f"Search ID not found   •   Time passed: {ts_end - ts_start:.2f}s")
            
            await interaction.followup.send(embed=summary_embed)
        else:
            records = results_data.get("records", [])
            total_results = results_data.get("total_results", 0)
            ts_start = results_data.get("timestamp_start", 0)
            ts_end = results_data.get("timestamp_end", time.time())

            summary_embed = discord.Embed(title="✅  Search Query Results", description=f"A search has returned total of {total_results}.", color=discord.Color.dark_teal())
            summary_embed.add_field(name="📂 Total results:", value=f"*{total_results}*", inline=False)
            summary_embed.add_field(name="🔑 Query keyword:", value=f"*{query}*", inline=False)
            summary_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            summary_embed.set_footer(text=f"Successfully retrieved results   •   Time passed: {ts_end - ts_start:.2f}s")
            
            view = intelx_results(records, domain=query, author_id=interaction.user.id, page_size=1)
            first_page = view.update_embed(0)
            await interaction.followup.send(embed=summary_embed)
            await interaction.followup.send(embed=first_page, view=view)
            print(f"{bcolors.OKGREEN}[INTELX SEARCH COMPLETE]{bcolors.ENDC} Discord User-ID: {self.user_id}, Search Query: {query}, Results: {str(total_results)} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

    @discord.ui.button(label="Change amount of results", style=discord.ButtonStyle.secondary, emoji="⚙️", custom_id="set_amount")
    async def amount_set(self, button: discord.ui.Button, interaction: discord.Interaction):
        query = search_data[self.user_id]["query"]

        results_amount = discord.Embed(title="⚙️  Change amount of results", description=f"Please enter the desired amount of results:", color=discord.Color.dark_theme())
        results_amount.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        results_amount.set_footer(text=f"Default value is 10   •   Current query: {query}")
        await interaction.response.send_message(embed=results_amount, ephemeral=True )

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=15.0)
            results_amount = msg.content.strip()

            search_data[self.user_id] = search_data.get(self.user_id, {}) 
            search_data[self.user_id]["results_amount"] = results_amount
            query = search_data[self.user_id]["query"]

            results_change = discord.Embed(title="✔️  Successfully changed amount of results", description=f"You set results amount to *{results_amount}*", color=discord.Color.dark_green())
            results_change.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            results_change.set_footer(text=f"Current query: {query}")
            await interaction.followup.send(embed=results_change, ephemeral=True)


            query_embed = discord.Embed(title="🔎  Search Query", description=f"Your query: **{query}**\n Results amount (default): **{search_data[self.user_id]["results_amount"]}**", color=discord.Color.blurple())
            query_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            query_embed.set_footer(text=f"Waiting on user start   •   Current query: {query}")
            view = intelx_search(self.user_id)
            await interaction.followup.send(embed=query_embed, view=view)

        except Exception as e:
            if e != "":
                time_now = datetime.datetime.now(datetime.UTC)
                print(f"{bcolors.FAIL}[RESULTS CHANGE MALFUNCTION]{bcolors.ENDC} Error while changing amount of results: {bcolors.UNDERLINE}{e}{bcolors.ENDC} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

            timeout_embed = discord.Embed(title="⏰  Timeout", description=f"Timeout while waiting for input.", color=discord.Color.dark_red())
            timeout_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            await interaction.followup.send(embed=timeout_embed, ephemeral=True)

# ============================
#       HaveIBeenPwned
# ============================
class hibp_search(discord.ui.View):
        def __init__(self, user_id: int):
            super().__init__(timeout=None)
            self.user_id = user_id

        @discord.ui.button(label="Search", style=discord.ButtonStyle.primary, emoji="🔍", custom_id="search")
        async def search_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            data = search_data.get(self.user_id, {})

            email_query = data.get("email_query", "n/a")
            time_now = datetime.datetime.now(datetime.UTC)

            ts_start = data.get("timestamp_start", 0)
            ts_end = data.get("timestamp_end", time.time())

            print(f"{bcolors.OKCYAN}[HIBP SEARCH START]{bcolors.ENDC} Discord User-ID: {self.user_id}, Search Query: {email_query} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
            
            started_embed = discord.Embed(title="🕓  Email Lookup Started", description=f"An email lookup ({email_query}) has started.", color=discord.Color.blurple())
            started_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            started_embed.set_footer(text=f"Search started by {self.user_id} on {time_now.strftime("%c")}(UTC)")

            await interaction.response.send_message(embed=started_embed)

            results_data = await asyncio.to_thread(handler.hibp_search, email_query)
            
            if results_data.get("status", 0) == 1:
                ts_start = results_data.get("timestamp_start", 0)
                ts_end = results_data.get("timestamp_end", time.time())

                summary_embed = discord.Embed(title="❌  No results", description=f"Am email lookup has returned total of 0 results.", color=discord.Color.dark_red())
                summary_embed.add_field(name="📂 Total results:", value=f"*0*", inline=False)
                summary_embed.add_field(name="🔑 Query keyword:", value=f"*{email_query}*", inline=False)
                summary_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
                summary_embed.set_footer(text=f"No results found for the query   •   Time passed: {ts_end - ts_start:.2f}s")
                
                await interaction.followup.send(embed=summary_embed)
            elif results_data.get("status", 0) == 2:
                print(f"{bcolors.FAIL}[HIBP SEARCH MALFUNCTION]{bcolors.ENDC} Your email lookup has stumbled on a problem while trying to run. Check previous LOG information. | Discord User-ID: {self.user_id}, Search Query: {email_query} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

                ts_start = results_data.get("timestamp_start", 0)
                ts_end = results_data.get("timestamp_end", time.time())

                summary_embed = discord.Embed(title="❌  Search Error", description=f"Your email lookup has stumbled on a problem while trying to run. Try again or see logs.", color=discord.Color.dark_red())
                summary_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
                summary_embed.set_footer(text=f"Error while running email lookup   •   Time passed: {ts_end - ts_start:.2f}s")
                
                await interaction.followup.send(embed=summary_embed)
            else:
                breach_records = results_data.get("result")

                isStealer = results_data.get("isStealer")
                stealer_status = isStealer.get("status", False)
                stealer_records = results_data.get("stealer_domains")

                results_count = 0
                for record in breach_records:
                    results_count += 1

                summary_embed = discord.Embed(title="✅  Search Query Results", description=f"An email lookup has returned total of {results_count}.", color=discord.Color.dark_teal())
                summary_embed.add_field(name="📂 Total results:", value=f"*{results_count}*", inline=False)
                summary_embed.add_field(name="🔑 Query keyword:", value=f"*{email_query}*", inline=False)
                summary_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
                summary_embed.set_footer(text=f"Successfully retrieved results   •   Time passed: {ts_end - ts_start:.2f}s")
                
                view = hibp_results(breach_records, stealer_records, isStealer, email=email_query, author_id=interaction.user.id, page_size=1)

                first_page = view.update_embed(0)
                await interaction.followup.send(embed=summary_embed)
                await interaction.followup.send(embed=first_page, view=view)
                print(f"{bcolors.OKGREEN}[HIBP LOOKUP COMPLETE]{bcolors.ENDC} Discord User-ID: {self.user_id}, Search Query (email): {email_query}, Results: {str(results_count)} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
class hibp_results(discord.ui.View):
    def __init__(self, records, stealer_records, isStealer, email, author_id, page_size=1):
        super().__init__(timeout=None)
        self.records = records
        self.stealer_records = stealer_records
        self.isStealer = isStealer
        self.email = email
        self.author_id = author_id
        self.page_size = page_size
        self.current_page = 0
        self.total_pages = max(1, (len(self.records) + page_size - 1) // page_size)
        self.update_label()

    @discord.ui.button(label="Download results (JSON)", style=discord.ButtonStyle.secondary, emoji="📦", custom_id="download_results")
    async def download_results(self, button: discord.ui.Button, interaction: discord.Interaction):
        time_now = datetime.datetime.now(datetime.UTC)

        if interaction.user.id != self.author_id: # discord userid check
            incorrect_embed = discord.Embed(title="❌  Restricted Access", description=f"You cannot download someone else's search results.", color=discord.Color.darkred())
            incorrect_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            await interaction.response.send_message(embed=incorrect_embed, ephemeral=True)
            return

        results_file = BytesIO(json.dumps({"records": self.records}, indent=4).encode("utf-8"))
        file = discord.File(results_file, filename=f"results-hibp[{self.email}].json")

        results_embed = discord.Embed(title="📦  Search Results", description=f"Here are your email lookup results in the JSON format (.json)", color=discord.Color.gold())
        results_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        results_embed.set_footer(text="Below you can see the results file in json.")

        await interaction.response.send_message(embed=results_embed, ephemeral=True)
        await interaction.followup.send(file=file, ephemeral=True)

        print(f"{bcolors.WARNING}[HIBP LOOKUP RESULTS DOWNLOAD]{bcolors.ENDC} Search results downloaded | Discord User-ID: {self.author_id} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary, custom_id="previous_page")
    async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
        
        if interaction.user.id != self.author_id: # discord userid check
            incorrect_embed = discord.Embed(title="❌  Restricted Access", description=f"You cannot control someone else's pagination.", color=discord.Color.darkred())
            incorrect_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            await interaction.response.send_message(embed=incorrect_embed, ephemeral=True)
            return

        if self.current_page > 0:
            self.current_page -= 1
        embed = self.update_embed(self.current_page)
        self.update_label()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="1/1", style=discord.ButtonStyle.gray, disabled=True, custom_id="page_number")
    async def page_display(self, button: discord.ui.Button, interaction: discord.Interaction):
        navigation_embed = discord.Embed(title="❔  Navigation", description=f"Use the arrows to navigate.", color=discord.Color.lightgrey())
        navigation_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        await interaction.response.send_message(embed=navigation_embed, ephemeral=True)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary, custom_id="next_page")
    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):

        if interaction.user.id != self.author_id: # discord userid check
            incorrect_embed = discord.Embed(title="❌  Restricted Access", description=f"You cannot control someone else's pagination.", color=discord.Color.darkred())
            incorrect_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
            await interaction.response.send_message(embed=incorrect_embed, ephemeral=True)
            return

        if self.current_page < max(0, self.total_pages - 1):
            self.current_page += 1
        embed = self.update_embed(self.current_page)
        self.update_label()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_label(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.custom_id == "page_number":
                item.label = f"{self.current_page+1}/{self.total_pages}"
                break

    def update_embed(self, index: int):
        index = max(0, min(index, self.total_pages - 1))
        start_index = index * self.page_size
        end_index = start_index + self.page_size
        update_records = self.records[start_index:end_index]
        embed = discord.Embed(title=f"🗃️ Page {index+1} of search ({self.email})", description="", color=discord.Color.dark_theme())
        
        if not update_records:
            embed.add_field(name="No results on this page", value="", inline=False)
        else:
            for record in update_records:
                breach_name = record.get("Name", "n/a")
                breach_domain = record.get("Domain", "n/a")
                breach_date = record.get("BreachDate", "n/a")
                breach_verified = record.get("IsVerified", False)
                breach_logo = record.get("LogoPath", "")

                # Breach Types
                breach_stealerlog = record.get("IsStealerLog", False) 

                status = ""
                if breach_verified == True:
                    status = "✅"
                else:
                    status = "❌"

                if breach_stealerlog == False:
                    embed.add_field(name="Breach name:", value=f"*{breach_name}*", inline=False)
                    embed.add_field(name="Breached domain:", value=f"*{breach_domain}*", inline=False)
                    embed.add_field(name="Breach date:", value=f"*{breach_date}*", inline=False)
                    embed.add_field(name="Is the breach verified by HIBP?:", value=f"*{status}*", inline=False)
                    embed.set_image(url=f"{breach_logo}")
                else:
                    embed.add_field(name="Breach name:", value=f"*{breach_name}*", inline=False)
                    embed.add_field(name="Breached domains:", value=f"*{self.stealer_records}*", inline=False)
                    embed.add_field(name="Breach date:", value=f"*{breach_date}*", inline=False)
                    embed.add_field(name="Is the breach verified by HIBP?:", value=f"*{status}*", inline=False)
                    embed.set_image(url=f"{breach_logo}")

        embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        embed.set_footer(text=f"Page {index+1} of {self.total_pages}   •   Total results: {len(self.records)}")
        return embed


@bot.event
async def on_ready():
    os.system('cls')
    time_now = datetime.datetime.now(datetime.UTC)
    print(f"{bcolors.WARNING}[BOT STATUS CHANGE]{bcolors.ENDC} {bot.user} is online | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")
    
    # Bot Statuses (https://www.pythondiscord.com/pages/guides/python-guides/setting-different-statuses-on-your-bot/)
    # Additional Info: https://discordpy.readthedocs.io/en/stable/api.html?highlight=discord%20activity#discord.Activity
    for guild in bot.guilds:
        # Listening Activity
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(  name='Databreach forensics', 
                                        details="", 
                                        state="Performing searches on IntelX",
                                        type=discord.ActivityType.listening ))

@bot.slash_command(name="domain", description="Perform a domain search for data breach lookup.")
async def domain_search(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="🔗  Data Breach Search", description="Please enter the search query to use for the data breach lookup.", color=discord.Colour.dark_theme())
    embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
    
    if os.getenv('BOT_WATERMARK') == "TRUE":
        embed.set_footer(text=f"Requested by @{ctx.author.id}   •   https://github.com/z3rodaycve/breachcord") 
    else:
        embed.set_footer(text=f"Requested by @{ctx.author.id}") 

    await ctx.respond(embed=embed)

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=15.0) 
        query = msg.content.strip()
        search_data[ctx.author.id] = {"query": query}
        search_data[ctx.author.id]["results_amount"] = 10 # default

        query_embed = discord.Embed(title="🔎  Search Query", description=f"Your query: **{query}**\n Results amount (default): **{search_data[ctx.author.id]["results_amount"]}**", color=discord.Color.blurple())
        query_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")

        if os.getenv('BOT_WATERMARK') == "TRUE":
            embed.set_footer(text=f"Requested by @{ctx.author.id}   •   https://github.com/z3rodaycve/breachcord") 
        else:
            embed.set_footer(text=f"Requested by @{ctx.author.id}") 
        
        view = intelx_search(ctx.author.id)
        await ctx.followup.send(embed=query_embed, view=view)

    except Exception as e:
        if e != "":
            time_now = datetime.datetime.now(datetime.UTC)
            print(f"{bcolors.FAIL}[USER INPUT MALFUNCTION]{bcolors.FAIL} Error while waiting for input: {bcolors.UNDERLINE}{e}{bcolors.ENDC} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

        timeout_embed = discord.Embed(title="⏰  Timeout", description="You didn't reply in time. Please re-run the command again.", color=discord.Color.red())
        timeout_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        await ctx.followup.send(embed=timeout_embed, ephemeral=True)

@bot.slash_command(name="email", description="Perform an email search for data breach lookup.")
async def email_search(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="📧  Email Lookup", description="Please enter an email address to use for the email lookup.", color=discord.Colour.dark_theme())
    embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
    
    if os.getenv('BOT_WATERMARK') == "TRUE":
        embed.set_footer(text=f"Requested by @{ctx.author.id}   •   https://github.com/z3rodaycve/breachcord") 
    else:
        embed.set_footer(text=f"Requested by @{ctx.author.id}") 

    await ctx.respond(embed=embed)

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=15.0) 

        email_query = msg.content.strip()
        search_data[ctx.author.id] = {"email_query": email_query}

        query_embed = discord.Embed(title="🔎  Email Lookup Query", description=f"Your query: **{email_query}**", color=discord.Color.blurple())
        query_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")

        if os.getenv('BOT_WATERMARK') == "TRUE":
            embed.set_footer(text=f"Requested by @{ctx.author.id}   •   https://github.com/z3rodaycve/breachcord") 
        else:
            embed.set_footer(text=f"Requested by @{ctx.author.id}") 
        
        view = hibp_search(ctx.author.id)
        await ctx.followup.send(embed=query_embed, view=view)

    except Exception as e:
        if e != "":
            time_now = datetime.datetime.now(datetime.UTC)
            print(f"{bcolors.FAIL}[EMAIL SEARCH INPUT MALFUNCTION]{bcolors.FAIL} Error while waiting for input: {bcolors.UNDERLINE}{e}{bcolors.ENDC} | {bcolors.BOLD}[{time_now.strftime("%c")}]{bcolors.ENDC} UTC")

        timeout_embed = discord.Embed(title="⏰  Timeout", description="You didn't reply in time. Please re-run the command again.", color=discord.Color.red())
        timeout_embed.set_author(name=f"{bot_name}", icon_url=f"{bot_photo}")
        await ctx.followup.send(embed=timeout_embed, ephemeral=True)

bot.run(os.getenv('BOT_TOKEN'))