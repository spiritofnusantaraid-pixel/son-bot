Trus kode yang ini?
import discord
from discord.ext import commands
import os
import json
import calendar
import asyncio
from datetime import date, datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "son_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"jadwal": {}, "undangan": {}}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

DATA = load_data()

@bot.event
async def on_ready():
    print(f"SON Bot Online: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# ============================================================
# ========== JADWAL INVITATION SON - NOVEMBER 2026 ==========
# ============================================================

def nama_hari_indo(tahun, bulan, tanggal):
    hari = date(tahun, bulan, tanggal).weekday()
    return ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][hari]

def buat_embed_jadwal(tahun=2026, bulan=11):
    nama_bulan = ["", "JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"][bulan]
    total_hari = calendar.monthrange(tahun, bulan)[1]
    teks = f"*INVITATION SON {nama_bulan} {tahun}*\n"
    for tgl in range(1, total_hari + 1):
        hari = nama_hari_indo(tahun, bulan, tgl)
        key = f"{tahun}-{bulan:02d}-{tgl:02d}"
        event = DATA.get("jadwal", {}).get(key)
        if event:
            teks += f"- {tgl} {nama_bulan.title()} {tahun}, {hari} : {event['nama']} , {event['jam']}✅\n"
        else:
            teks += f"- {tgl} {nama_bulan.title()} {tahun}, {hari}\n"
    embed = discord.Embed(title=f"📅 INVITATION SON — {nama_bulan} {tahun}", description=f"```\n{teks}\n```", color=0xFF0000) # Merah SON
    embed.set_footer(text="SPIRIT OF NUSANTARA • SON")
    return embed

class TambahJadwalModal(discord.ui.Modal, title="Tambah Jadwal SON"):
    tanggal_input = discord.ui.TextInput(label="Tanggal (1-31)", placeholder="Contoh: 6", required=True, max_length=2)
    nama_input = discord.ui.TextInput(label="Nama Event / Party", placeholder="Contoh: PARTY RIMEX", required=True, max_length=50)
    jam_input = discord.ui.TextInput(label="Jam", placeholder="Contoh: 9.00 WIB / 7 PM TILL DROP", required=True, max_length=30)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            tgl = int(self.tanggal_input.value.strip())
            key = f"2026-11-{tgl:02d}"
            DATA.setdefault("jadwal", {})[key] = {"nama": self.nama_input.value.strip(), "jam": self.jam_input.value.strip()}
            save_data(DATA)
            await interaction.response.send_message(f"✅ Jadwal SON ditambah!\n**{tgl} Nov 2026 : {self.nama_input.value} , {self.jam_input.value}✅**", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Tanggal salah! Isi angka aja, contoh: 6", ephemeral=True)

class HapusJadwalModal(discord.ui.Modal, title="Hapus Jadwal SON"):
    tanggal_input = discord.ui.TextInput(label="Tanggal yang mau dihapus", placeholder="Contoh: 6", required=True, max_length=2)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            tgl = int(self.tanggal_input.value.strip())
            key = f"2026-11-{tgl:02d}"
            if key in DATA.get("jadwal", {}):
                del DATA["jadwal"][key]
                save_data(DATA)
                await interaction.response.send_message(f"✅ Jadwal tanggal {tgl} dihapus!", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Tanggal {tgl} ga ada jadwalnya!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Tanggal salah!", ephemeral=True)

class JadwalSONView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="📅 Lihat Jadwal", style=discord.ButtonStyle.primary, custom_id="son_jadwal_lihat")
    async def lihat_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=buat_embed_jadwal(2026, 11), ephemeral=False)
    @discord.ui.button(label="➕ Tambah Jadwal", style=discord.ButtonStyle.green, custom_id="son_jadwal_tambah")
    async def tambah_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Cuma Admin / Owner SON!", ephemeral=True)
            return
        await interaction.response.send_modal(TambahJadwalModal())
    @discord.ui.button(label="🗑️ Hapus Jadwal", style=discord.ButtonStyle.red, custom_id="son_jadwal_hapus")
    async def hapus_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Cuma Admin / Owner SON!", ephemeral=True)
            return
        await interaction.response.send_modal(HapusJadwalModal())

# ============================================================
# ========== UNDANGAN EVENT SON ==========
# ============================================================

class BuatUndanganSONModal(discord.ui.Modal, title="Buat Undangan SON"):
    nama_input = discord.ui.TextInput(label="Nama Event / Party", placeholder="Contoh: PARTY RIMEX", required=True, max_length=50)
    link_input = discord.ui.TextInput(label="Link Map / Lokasi", placeholder="https://www.roblox.com/games/...", required=True, max_length=200)
    jam_input = discord.ui.TextInput(label="Jam", placeholder="Contoh: 20.00 WIB", required=True, max_length=30)
    tanggal_input = discord.ui.TextInput(label="Tanggal", placeholder="Contoh: 6 Nov 2026", required=True, max_length=30)
    catatan_input = discord.ui.TextInput(label="Catatan", placeholder="Contoh: Dresscode merah, kumpul lobby 1", required=False, style=discord.TextStyle.paragraph, max_length=200)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        view = UndanganSONView(nama=self.nama_input.value.strip(), link=self.link_input.value.strip(), jam=self.jam_input.value.strip(), tanggal=self.tanggal_input.value.strip(), catatan=self.catatan_input.value.strip(), pembuat=interaction.user)
        msg = await interaction.followup.send(embed=view.buat_embed(), view=view)
        DATA.setdefault("undangan", {})[str(msg.id)] = {"nama": view.nama, "peserta": []}
        save_data(DATA)
        await interaction.followup.send(f"✅ Undangan **{view.nama}** berhasil dibuat!", ephemeral=True)

class UndanganSONView(discord.ui.View):
    def __init__(self, nama="Event SON", link="-", jam="-", tanggal="-", catatan="", pembuat=None):
        super().__init__(timeout=None)
        self.nama = nama
        self.link = link
        self.jam = jam
        self.tanggal = tanggal
        self.catatan = catatan
        self.pembuat = pembuat
        self.peserta_ids = []
    def buat_embed(self):
        total = len(self.peserta_ids)
        list_p = "\n".join([f"{i+1}. <@{uid}>" for i, uid in enumerate(self.peserta_ids[:20])]) if self.peserta_ids else "Belum ada yang ikut, jadi yang pertama yuk! 🔥"
        desc = f"**🎉 Event :** {self.nama}\n**📅 Tanggal :** {self.tanggal}\n**⏰ Jam :** {self.jam}\n**🔗 Link :** [Klik Disini Buat Join]({self.link})\n"
        if self.catatan:
            desc += f"\n**📝 Catatan :**\n> {self.catatan}\n"
        desc += f"\n**👥 Yang Ikut ({total}) :**\n{list_p}"
        embed = discord.Embed(title="🔥 UNDANGAN SON — SPIRIT OF NUSANTARA", description=desc, color=0xFF0000)
        embed.set_footer(text="SPIRIT OF NUSANTARA • SON")
        return embed
    @discord.ui.button(label="✅ Ikut", style=discord.ButtonStyle.green, custom_id="son_ikut")
    async def ikut_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.peserta_ids:
            await interaction.response.send_message("❌ Kamu udah ikut!", ephemeral=True)
            return
        self.peserta_ids.append(interaction.user.id)
        await interaction.response.edit_message(embed=self.buat_embed(), view=self)
        await interaction.followup.send(f"✅ {interaction.user.mention} ikut **{self.nama}**! 🔥", ephemeral=True)
    @discord.ui.button(label="❌ Ga Bisa", style=discord.ButtonStyle.red, custom_id="son_gabisa")
    async def gabisa_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.peserta_ids:
            self.peserta_ids.remove(interaction.user.id)
            await interaction.response.edit_message(embed=self.buat_embed(), view=self)
            await interaction.followup.send("Oke, dihapus dari list!", ephemeral=True)
        else:
            await interaction.response.send_message("Oke, noted ga bisa!", ephemeral=True)
    @discord.ui.button(label="📋 Tag Semua Yang Ikut", style=discord.ButtonStyle.blurple, custom_id="son_tag")
    async def tag_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Cuma Admin / Owner!", ephemeral=True)
            return
        if not self.peserta_ids:
            await interaction.response.send_message("❌ Belum ada yang ikut!", ephemeral=True)
            return
        mentions = " ".join([f"<@{uid}>" for uid in self.peserta_ids])
        await interaction.response.send_message(f"📣 **PING! Waktunya {self.nama}!**\n📅 {self.tanggal} | ⏰ {self.jam}\n🔗 {self.link}\n\n{mentions}\n\nGas kuy! 🔥")

# ============================================================
# ========== PANEL & SETUP SON ==========
# ============================================================

class SONPanelLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        container = discord.ui.Container(accent_color=0xFF0000)
        container.add_item(discord.ui.TextDisplay(
            f"## 🔥 SPIRIT OF NUSANTARA • SON\n"
            f"✦ ───────────────────── ✦\n"
            f"**Selamat datang di SON!** 🇮🇩\n\n"
            f"Disini tempat semua jadwal party, mabar, dan event SON.\n\n"
            f"**✨ Cara Pakai:**\n"
            f"> Liat jadwal bulanan di bawah\n"
            f"> Pencet `✅ Ikut` kalo mau ikut event\n"
            f"✦ ───────────────────── ✦"
        ))
        container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))
        row = discord.ui.ActionRow()
        btn1 = discord.ui.Button(label="LIHAT JADWAL", style=discord.ButtonStyle.primary, emoji="📅", custom_id="son_panel_jadwal")
        async def jadwal_cb(interaction: discord.Interaction):
            await interaction.response.send_message(embed=buat_embed_jadwal(2026, 11), ephemeral=False)
        btn1.callback = jadwal_cb
        row.add_item(btn1)
        btn2 = discord.ui.Button(label="BUAT UNDANGAN", style=discord.ButtonStyle.success, emoji="🔥", custom_id="son_panel_buat")
        async def buat_cb(interaction: discord.Interaction):
            if not interaction.user.guild_permissions.administrator and interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message("❌ Cuma Admin / Owner SON!", ephemeral=True)
                return
            await interaction.response.send_modal(BuatUndanganSONModal())
        btn2.callback = buat_cb
        row.add_item(btn2)
        container.add_item(row)
        container.add_item(discord.ui.TextDisplay("-# 🔥 SPIRIT OF NUSANTARA • SON"))
        self.add_item(container)

@bot.tree.command(name="jadwal-son", description="Lihat jadwal SON November 2026")
async def jadwal_son(interaction: discord.Interaction):
    await interaction.response.send_message(embed=buat_embed_jadwal(2026, 11))

@bot.tree.command(name="tambah-jadwal-son", description="Tambah jadwal SON (Admin / Owner)")
async def tambah_jadwal_son(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Cuma Admin / Owner SON!", ephemeral=True)
        return
    await interaction.response.send_modal(TambahJadwalModal())

@bot.tree.command(name="buat-undangan-son", description="Buat undangan event SON (Admin / Owner)")
async def buat_undangan_son(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Cuma Admin / Owner SON!", ephemeral=True)
        return
    await interaction.response.send_modal(BuatUndanganSONModal())

@bot.tree.command(name="setup-son", description="Bikin channel SON (Owner only)")
async def setup_son(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Hanya Owner!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    guild = interaction.guild
    # Hapus channel lama SON kalo ada
    for ch in list(guild.channels):
        if ch.name in ["jadwal-son", "undangan-son", "📅┆・jadwal-son", "🔥┆・undangan-son", "🇮🇩┆・son"]:
            try: await ch.delete()
            except: pass
    ch1 = await guild.create_text_channel("📅┆・jadwal-son")
    ch2 = await guild.create_text_channel("🔥┆・undangan-son")
    await ch1.send(view=SONPanelLayout())
    msg = await ch1.send(embed=buat_embed_jadwal(2026, 11), view=JadwalSONView())
    try: await msg.pin()
    except: pass
    await ch2.send(view=SONPanelLayout())
    await interaction.followup.send(f"✅ Berhasil! Bot SON udah di-setup!\n{ch1.mention} + {ch2.mention}", ephemeral=True)

@bot.event
async def setup_hook():
    try:
        bot.add_view(JadwalSONView())
        bot.add_view(SONPanelLayout())
        bot.add_view(UndanganSONView())
    except Exception as e:
        print(f"setup_hook error: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
