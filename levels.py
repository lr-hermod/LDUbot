import discord
from discord.ext import commands, tasks
import json
import yaml
import random
import math
import os
import copy

import discord
from discord.ext import commands
import yaml
import os
import copy

class ConfigHandler:
    guilds = {}
    defaultconfig = {
        "base": 50,
        "growth_rate": 1.2,
        "point_range_upper": 5,
        "point_range_lower": 1,
        "roles": {}
    }

    def __init__(self, guild: discord.Guild):
        self.guildid = guild.id
        self.guildname = guild.name
        self.config = {}

        self.config = self.load()
        print(f"config for {self.guildid} ({self.guildname}) loaded:\n{self.config}")
        
        if self.guildid not in ConfigHandler.guilds:
            ConfigHandler.guilds[self.guildid] = self


    def save(self):
        dir_path = f"savedata/{self.guildid}"
        file_path = f"{dir_path}/config.yml"

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        try:
            with open(file_path, "w") as file:
                yaml.dump(self.config, file)
        except Exception as e:
            print(f"Failed to save config for guild {self.guildid}: {e}")

    def load(self):
        if not os.path.exists(f"savedata/{self.guildid}/config.yml"):
            self.config = copy.deepcopy(ConfigHandler.defaultconfig)
            self.save()
        else:
            with open(f"savedata/{self.guildid}/config.yml", "r") as file:
                self.config = yaml.safe_load(file)
        return self.config

    def setconfig(self, key, value):
        self.config[key] = value
        self.save()
        return self.config[key]

    def getconfig(self, key: str):
        """ get a config value by key """
        return self.config.get(key, None)

    def delconfig(self, key):
        if key in self.config:
            del self.config[key]
            self.save()
            self.load()

    def set_level_role(self, level: int, role: discord.Role):
        roleid = role.id
        self.config["roles"][level] = roleid
        self.save()
        return self.config["roles"][level]
    
    def del_level_role(self, level: int):
        if level in self.config["roles"]:
            del self.config["roles"][level]
            self.save()
            self.load()


pointspath = "savedata/points.json"

class GuildConfig(commands.GroupCog, group_name="config"):
    def __init__(self, client: commands.Bot):
        self.client = client

        for guild in self.client.guilds:
            if guild.id not in ConfigHandler.guilds:
                ConfigHandler(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.id not in ConfigHandler.guilds:
            ConfigHandler(guild)
        print(f"Joined guild: {guild.name} (ID: {guild.id})")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if guild.id in ConfigHandler.guilds:
            del ConfigHandler.guilds[guild.id]
        print(f"Left guild: {guild.name} (ID: {guild.id})")

    @discord.app_commands.command(
        name="set_base", description=f"set the amount of points to get from level 0 to level 1 (default: {ConfigHandler.defaultconfig['base']})"
    )
    async def set_base(self, interaction: discord.Interaction, base: int):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        guild_config.setconfig("base", base)
        await interaction.response.send_message(f"set base points amount to {base}")

    @discord.app_commands.command(name="get_base", description="get the amount of points to get from level 0 to level 1")
    async def get_base(self, interaction: discord.Interaction):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        base = guild_config.getconfig("base")
        await interaction.response.send_message(f"base points amount is {base}")

    @discord.app_commands.command(name="set_growth_rate", description=f"set the growth rate for points (default: {ConfigHandler.defaultconfig['growth_rate']})")
    async def set_growth_rate(self, interaction: discord.Interaction, rate: float):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        guild_config.setconfig("growth_rate", rate)
        await interaction.response.send_message(f"set growth rate to {rate}")

    @discord.app_commands.command(name="get_growth_rate", description="get the growth rate for points")
    async def get_growth_rate(self, interaction: discord.Interaction):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        rate = guild_config.getconfig("growth_rate")
        await interaction.response.send_message(f"growth rate is {rate}")

    @discord.app_commands.command(name="set_point_range", description=f"set the upper and lower bound for points awarded (default: {ConfigHandler.defaultconfig['point_range_lower']} - {ConfigHandler.defaultconfig['point_range_upper']})")
    async def set_point_range(self, interaction: discord.Interaction, lower: int, upper: int):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        guild_config.setconfig("point_range_lower", lower)
        guild_config.setconfig("point_range_upper", upper)
        await interaction.response.send_message(f"set point range to {lower} - {upper}")

    @discord.app_commands.command(name="get_point_range", description="get the upper and lower bound for points awarded")
    async def get_point_range(self, interaction: discord.Interaction):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        lower = guild_config.getconfig("point_range_lower")
        upper = guild_config.getconfig("point_range_upper")
        await interaction.response.send_message(f"point range is {lower} - {upper}")

    @discord.app_commands.command(name="reset_config", description="reset the configuration for this guild")
    async def reset_config(self, interaction: discord.Interaction):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        guild_config.load()
        await interaction.response.send_message("configuration reset")

    @discord.app_commands.command(name="get_config", description="get the configuration for this guild")
    async def get_config(self, interaction: discord.Interaction):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        
        config = guild_config.config
        roles = config["roles"]
        upd_roles = {}

        if roles != {}:
            for level, role in roles.items():
                role = interaction.guild.get_role(role)
                upd_roles[level] = role.name
        else:
            upd_roles = "No roles set (use /config set_level_role <level> <role> to set a role)"

        config["roles"] = upd_roles
        
        yaml_config = yaml.dump(config)


        await interaction.response.send_message(f"configuration for {interaction.guild.name}:\n```yaml\n{yaml_config}```")

    @discord.app_commands.command(name="set_level_role", description="set a role to be awarded at a certain level")
    @commands.has_permissions(manage_roles=True)
    async def set_level_role(self, interaction: discord.Interaction, level: int, role: discord.Role):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        guild_config.set_level_role(level, role)
        await interaction.response.send_message(f"role {role.name} set to be awarded at level {level}")

    @discord.app_commands.command(name="del_level_role", description="remove a role from being awarded at a certain level")
    @commands.has_permissions(manage_roles=True)
    async def del_level_role(self, interaction: discord.Interaction, level: int):
        guild_config = ConfigHandler.guilds.get(interaction.guild.id)
        if not guild_config:
            await interaction.response.send_message("configuration not found for this guild.")
            return
        role_name = guild_config.config["roles"].get(level, "role not found")
        guild_config.del_level_role(level)
        await interaction.response.send_message(f"role {role_name} removed from level {level}")


async def setup(client: commands.Bot):
    await client.add_cog(GuildConfig(client))


class Levels(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.points = self.load_points()
        self.save_task.start()
        self.recentmessages = {}
        self.default_growth_rate = 1.2
        self.default_point_range_upper = 5
        self.default_point_range_lower = 1
        self.emojis = {
            0: ":first_place:",
            1: ":second_place:",
            2: ":third_place:",
            3: ":four:",
            4: ":five:",
            5: ":six:",
            6: ":seven:",
            7: ":eight:",
            8: ":nine:",
            9: ":keycap_ten:"
        }
        self.otheremoji = ":speech_balloon:"

    def get_level_from_points(self, points, guild_id):
        if type(guild_id) != int:
            try:
                guild_id = int(guild_id)
            except ValueError:
                print(f"Error converting guild_id {guild_id} to int")
        guild = ConfigHandler.guilds[guild_id]
        base = guild.getconfig("base")
        growth_rate = guild.getconfig("growth_rate")

        level = 0
        required = base
        counted = 0

        while points >= required:
            counted += 1
            if counted == required:
                level += 1
                required = math.floor(required * growth_rate)
                counted = 0  

        remaining_points = required - counted  

        return level, remaining_points
        

        

    def add_recent_sender(self, guild, user):
        if guild not in self.recentmessages.keys():
            self.recentmessages[guild] = []
        if user not in self.recentmessages[guild]:
            self.recentmessages[guild].append(user)

    def is_recent_sender(self, guild, user):
        if guild not in self.recentmessages.keys():
            return False
        if user in self.recentmessages[guild]:
            return True
        return False
    
    def award_points(self, guild, user, points):
        if guild not in self.points.keys():
            self.points[guild] = {}
        if user not in self.points[guild]:
            self.points[guild][user] = 0
        self.points[guild][user] += points

    def load_points(self):
        if os.path.exists(pointspath):
            try:
                with open(pointspath, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("Error loading points.json: resetting data.")
                return {}
        return {}

    def save_points(self):
        with open(pointspath, "w") as file:
            json.dump(self.points, file, indent=2)
            self.recentmessages = {}

    def reset_guild_points(self, guild):
        self.points[guild] = {}
        self.save_points()

    @tasks.loop(seconds=30)  # save every 30 seconds
    async def save_task(self):
        self.save_points()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Levels cog ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        guildconfig = ConfigHandler.guilds[message.guild.id]
        guildid = str(message.guild.id)
        print(f"message received in {guildid}")
        if guildconfig is None:
            print(f"ConfigHandler.guilds[{guildid}] is None!")
            point_range_lower = self.default_point_range_lower
            point_range_upper = self.default_point_range_upper
        else:
            point_range_lower = guildconfig.getconfig("point_range_lower")
            point_range_upper = guildconfig.getconfig("point_range_upper")


        random.seed(message.id)
        award = random.randint(point_range_lower, point_range_upper)
        if message.author.bot or message.guild is None:
            return
        guild_id = str(message.guild.id)
        author_id = str(message.author.id)
        guild_name = message.guild.name

        if self.is_recent_sender(guild_id, author_id):
            stamp = f"{guild_name}: recent sender {message.author.name} not awarded points"
            print(stamp)
            return
        else:
            self.add_recent_sender(guild_id, author_id)
            stamp = f"{guild_name}: awarding {message.author.name} {award} points"
            self.award_points(guild_id, author_id, award)
            print(stamp)
        

    @discord.app_commands.command(name="get_level", description="fetch the level of a user")
    async def get_points(self, interaction: discord.Interaction, user: discord.Member=None):
        targetisinvoker = False

        if user is None or user == interaction.user:
            targetisinvoker = True
            user = interaction.user
        print(f"{interaction.user.name} invoked get_level on {user.name}")
        if interaction.guild is None:
            await interaction.response.send_message("this command must be used in a server!")
            return
        
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        points = self.points.get(guild_id, {}).get(user_id, 0)
        level, tonextlevel = self.get_level_from_points(points, guild_id)
        stamp = f"level {level} ({points} points) with {tonextlevel - points} points until next level"
        if targetisinvoker:
            await interaction.response.send_message(f"you are {stamp}")
        else:
            await interaction.response.send_message(f"{user.mention} is {stamp}")



    @discord.app_commands.command(name="get_leaderboard", description="fetch the top users by points")
    async def get_leaderboard(self, interaction: discord.Interaction, pages: int=1):
        if interaction.guild is None:
            await interaction.response.send_message("this command must be used in a server!")
            return
        guild_id = str(interaction.guild.id)
        guild_name = interaction.guild.name
        points = self.points.get(guild_id, {})
        sortedpoints = sorted(points.items(), key=lambda x: x[1], reverse=True) # sort users by points
        leaderboard = [] #
        for i, (user_id, user_points) in enumerate(sortedpoints):
            username = interaction.guild.get_member(int(user_id))
            if username is None:
                username = "could not resolve username"
            username = username.name
            level, tonextlevel = self.get_level_from_points(user_points, guild_id)

            if i in self.emojis.keys():
                emoji = self.emojis.get(i, "")
            else:
                emoji = self.otheremoji

            leaderboard.append(f"{emoji} `[Level {level}]` **{username}** `{user_points} points, {tonextlevel - user_points} to next level`")
        header = f"# `Leaderboard for {guild_name}`"
        leaderboard = leaderboard[:(pages * 10)]
        
        leaderboard = '\n'.join(leaderboard)
        leaderboard = header + '\n' + leaderboard
        
        leaderboard = leaderboard + f"\n-# (max items: {pages * 10})"
        await interaction.response.send_message(leaderboard)

    @discord.app_commands.command(name="reset_points", description="reset the points for the whole server")
    @commands.has_permissions(manage_guild=True)
    async def reset_points(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("this command must be used in a server!")
            return
        guild_id = str(interaction.guild.id)
        self.reset_guild_points(guild_id)
        await interaction.response.send_message(f"points for guild {interaction.guild.name} reset")

        
async def setup(client):
    levels_cog = Levels(client)
    guild_config_cog = GuildConfig(client)

    await client.add_cog(levels_cog)
    await client.add_cog(guild_config_cog)

    print('Cogs "levels" and "guild_config" loaded')

