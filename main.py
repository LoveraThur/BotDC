import os
import discord as dc
from discord.ext import commands
from discord import app_commands
import ccxt
import yt_dlp
import asyncio
from collections import deque
from dotenv import load_dotenv




intents = dc.Intents.default()
intents.members = True

intents = dc.Intents.all()

bot = commands.Bot(".", intents=intents)

load_dotenv()

TOKEN = os.getenv("token")




GUILD_ID = os.getenv("guild_id")


@bot.event
async def on_ready():
    sincs = await bot.tree.sync()
    print(f'{len(sincs)} sincs Inicializadas')
    await bot.change_presence(activity=dc.Game('Terminal'))
    music_guild = dc.Object(id=GUILD_ID)
    await bot.tree.sync(guild=music_guild)
    

async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda:_extract(query, ydl_opts))

def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)


@bot.event
async def on_member_join(membro: dc.Member):
    canal = bot.get_channel(int(os.getenv("welcome_channel")))
    minha_embed = dc.Embed()
    minha_embed.title = f'Welcome {membro.name}!'
    minha_embed.description = f'Thanks for join in server  {membro.mention}. Have a good experience!'

    role = dc.utils.get(membro.guild.roles, name = 'Betas')
    await membro.add_roles(role)

    img = dc.File('imagens/welcome.jpg', 'welcome.jpg')
    minha_embed.set_image(url='attachment://welcome.jpg')

    await canal.send(embed=minha_embed, file=img)


@bot.command()
async def bitcoin(ctx: commands.Context):
    canal = bot.get_channel(int(os.getenv("principal_channel")))
    def formatar_brl(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


    exchange = ccxt.binance()

    ticker = exchange.fetch_ticker('BTC/BRL')

    preco = ticker['last']
    await canal.send(f"Preço atual do Bitcoin: {formatar_brl(preco)} BRL")

#musicas

SONG_QUEUES = {}


@bot.tree.command(name="play", description="Play a Song or add it to the queue")
@app_commands.describe(song_query="Search Song")
async def play(interaction: dc.Interaction, song_query: str):
    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel

    if voice_channel is None:
        await interaction.followup.send('Você não está em um canal de voz')
        return
    
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_channel != voice_client.channel:
        await voice_client.move_to(voice_channel)

    cookies_path = os.path.join(os.path.dirname(__file__), "cookies.txt")
    ydl_options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "source_address": "0.0.0.0",
        **({"cookiefile": cookies_path} if os.path.exists(cookies_path) else {})
    }


    query = f"ytsearch:{song_query}"
    results = await search_ytdlp_async(query, ydl_options)

    if results is None:
        await interaction.followup.send("Nenhum resultado encontrado")
        return
    

    if "entries" in results:
        if not results['entries']:
            await interaction.followup.send('Nenhum resultado encontrado')
            return

        first_track = results['entries'][0]
        webpage_url = first_track.get("webpage_url") or first_track.get("url")
        full_info = await search_ytdlp_async(webpage_url, ydl_options)
        audio_url = full_info["url"]
        title = first_track.get("title", "Untitled")
    
    else:
        audio_url = results["url"]
        title = results.get('title', 'Untitled')

    
    
    ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconect_delay_max 5",
            "options": "-vn"
    }

    source = dc.FFmpegPCMAudio(
        audio_url,
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    guild_id = str(interaction.guild_id)

    if guild_id not in SONG_QUEUES:
        SONG_QUEUES[guild_id] = deque()

    
    SONG_QUEUES[guild_id].append((audio_url, title))

    voice_client = interaction.guild.voice_client

    if voice_client.is_playing() or voice_client.is_paused():
        await interaction.followup.send(f"Adicionado na fila: **{title}**")
    else:
        await interaction.followup.send("🎵 Iniciando reprodução...")
        await play_next_song(voice_client, guild_id, interaction.channel)


@bot.tree.command(name="skip", description="pula a musica atual.")
async def skip(interaction: dc.Interaction):
    if interaction.guild.voice_client and (interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused()):
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Musica skipada.")
    else:
        await interaction.response.send_message("Nao há musica na fila")

@bot.tree.command(name="pause", description="Pausa a Musica que esta tocando no momento.")
async def pause(interaction: dc.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        return await interaction.response.send_message("Eu nao estou em um canal de voz.")
    
    if not voice_client.is_playing():
        return await interaction.response.send_message("Nao esta tocando musica no momento!")

    voice_client.pause()
    await interaction.response.send_message("Reproducao Pausada!")

@bot.tree.command(name="resume", description="retoma a musica pausada")
async def resume(interaction: dc.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        return await interaction.response.send_message("Eu nao estou em um canal de voz.")
    if not voice_client.is_paused():
        return await interaction.response.send_message("Nao ha musica pausada agora")
    
    voice_client.resume()
    await interaction.response.send_message("Musica retomada!")

@bot.tree.command(name="disconnect", description="Para a musica e limpa a fila")
async def stop(interaction: dc.Interaction):

    voice_client = interaction.guild.voice_client

    if not voice_client or not voice_client.is_connected():
        return await interaction.response.send_message("Eu nao estou em um canal de voz")
    
    guild_id_str = str(interaction.guild_id)

    await interaction.response.send_message("desconectando do chat de voz...")
    
    if guild_id_str in SONG_QUEUES:
        SONG_QUEUES[guild_id_str].clear()

    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    await voice_client.disconnect()


async def play_next_song(voice_client, guild_id, channel):
    if guild_id not in SONG_QUEUES or not SONG_QUEUES[guild_id]:
        await voice_client.disconnect()
        SONG_QUEUES[guild_id] = deque()
        return

    audio_url, title = SONG_QUEUES[guild_id].popleft()

    source = dc.FFmpegPCMAudio(
        audio_url,
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    def after_play(error):
        if error:
            print(f"Erro ao tocar {title}: {error}")
        asyncio.run_coroutine_threadsafe(play_next_song(voice_client, guild_id, channel), bot.loop)

    voice_client.play(source, after=after_play)
    asyncio.create_task(channel.send(f"Tocando agora: **{title}**"))







bot.run(TOKEN)