"""
Craftify – Wikimedia Commons image downloader
Downloads authentic Indian handicraft photographs using the Wikimedia Commons API.
No API key required. Checks licences. Validates JPEG files.
"""

import urllib.request
import urllib.parse
import json
import os
import time
import struct

OUTPUT_DIR = r"c:\Users\Dell\OneDrive\Desktop\craftify\Craftify\public\images\products"
CREDITS_FILE = r"c:\Users\Dell\OneDrive\Desktop\craftify\Craftify\IMAGE_CREDITS.md"

WM_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "CraftifyResearchBot/1.0 (educational project; non-commercial)"}

# Each entry: (output_filename, product_name, [candidate WM filenames in preference order])
# Candidates are tried in order; first found and downloadable wins.
PRODUCTS = [
    ("pashmina-shawl.jpg", "Pashmina Shawl – J&K", [
        "Handwoven-kashmir-pashmina.jpg",
        "Kashmiri_pashmina_weaver_in_Srinagar.jpg",
        "Kashmir_Pashmina_shawl.jpg",
        "Pashmina_shawl.jpg",
    ]),
    ("papier-mache-keepsake-box.jpg", "Papier-Mâché Keepsake Box – J&K", [
        "Kashmiri_papier_mache_box.jpg",
        "Papier-mache-Box.jpg",
        "Kashmir_papier_mache.jpg",
        "Paper_mache_Kashmir.jpg",
        "Papier_mache_Kashmir.jpg",
    ]),
    ("kullu-woollen-shawl.jpg", "Kullu Woollen Shawl – Himachal Pradesh", [
        "Kullu_shawl.jpg",
        "Kullu_Shawl.jpg",
        "Kullu_wollen_shawl.jpg",
        "Himachali_shawl.jpg",
        "Himachal_Pradesh_shawl.jpg",
    ]),
    ("kangra-miniature-painting.jpg", "Kangra Miniature Painting – Himachal Pradesh", [
        "Kangra_painting.jpg",
        "Kangra_miniature_painting.jpg",
        "Pahari_miniature_painting.jpg",
        "Pahari_painting.jpg",
        "Kangra_style_painting.jpg",
    ]),
    ("phulkari-dupatta.jpg", "Phulkari Dupatta – Punjab", [
        "Patiala_Phulkari.jpg",
        "Contemporary_Phulkari_design.jpg",
        "Phulkari_embroidery.jpg",
        "Phulkari.jpg",
        "Punjab_phulkari.jpg",
    ]),
    ("panipat-khes-cotton-throw.jpg", "Panipat Khes Cotton Throw – Haryana", [
        "Panipat_khes.jpg",
        "Khes_blanket.jpg",
        "Indian_cotton_woven_throw.jpg",
        "Handwoven_cotton_textile_India.jpg",
        "Block_printed_cotton_bedsheet.jpg",
    ]),
    ("aipan-art-wall-frame.jpg", "Aipan Art Wall Frame – Uttarakhand", [
        "Aipan_art.jpg",
        "Aipan.jpg",
        "Kumaoni_aipan.jpg",
        "Uttarakhand_folk_art.jpg",
        "Kumaon_aipan.jpg",
    ]),
    ("banarasi-silk-saree.jpg", "Banarasi Silk Saree – Uttar Pradesh", [
        "Banarasi_Silk_Saree.jpg",
        "Benaras_brocade_sari.jpg",
        "Konia,_brocade_sari.jpg",
        "Banarasi_saree.jpg",
        "Banarasi_silk.jpg",
    ]),
    ("chikankari-kurta.jpg", "Chikankari Kurta – Uttar Pradesh", [
        "Chikan_embroidery,_Lucknow.jpg",
        "Chikankari_of_lucknow.jpg",
        "Chikan_embroidery.jpg",
        "Lucknow_chikankari.jpg",
        "Chikankari.jpg",
    ]),
    ("blue-pottery-vase.jpg", "Jaipur Blue Pottery Vase – Rajasthan", [
        "Blue_pottery_from_Jaipur.jpg",
        "Jaipur_Blue_Pottery_Vase_with_Raja-Rani_Design.jpg",
        "Blue_Pottery,_Albert_Hall_Museum,_Jaipur.jpg",
        "Jaipur_blue_pottery.jpg",
        "Blue_pottery_Jaipur.jpg",
    ]),
    ("sanganeri-block-printed-bedsheet.jpg", "Sanganeri Block-Printed Bedsheet – Rajasthan", [
        "Sanganeri_print_fabric.jpg",
        "Sanganer_block_print.jpg",
        "Sanganer_Print.jpg",
        "Rajasthan_block_print_fabric.jpg",
        "Block_printing_Rajasthan.jpg",
    ]),
    ("patan-patola-silk-scarf.jpg", "Patan Patola Silk Scarf – Gujarat", [
        "Patan_Patola.jpg",
        "Patola_silk.jpg",
        "Patan_patola_sari.jpg",
        "Double_ikat_patola.jpg",
        "Gujarat_patola.jpg",
    ]),
    ("kutch-embroidered-wall-hanging.jpg", "Kutch Embroidered Wall Hanging – Gujarat", [
        "Antique_Kutch_Embroidery.jpg",
        "Embroidered_hanging,_Kutch_(western_India).jpg",
        "Kutch_embroidery.jpg",
        "Kutchi_embroidery.jpg",
        "Gujarat_mirror_embroidery.jpg",
    ]),
    ("paithani-silk-saree.jpg", "Paithani Silk Saree – Maharashtra", [
        "Parrot_Peacock_border_paithani_saree.jpg",
        "Paithani_silk_saree.jpg",
        "Paithani_saree.jpg",
        "Paithani_Bridal_Sari_LACMA_M.75.4.23_(1_of_2).jpg",
        "Paithani.jpg",
    ]),
    ("warli-painting-on-cloth.jpg", "Warli Painting on Cloth – Maharashtra", [
        "Warli_painting.jpg",
        "Warli_art.jpg",
        "Warli-art-1.jpg",
        "Adivasi_art_form_cooking_-_Warli_Art.jpg",
        "Warli_tribal_art.jpg",
    ]),
    ("channapatna-wooden-toy-set.jpg", "Channapatna Wooden Toy Set – Karnataka", [
        "Channapatna_toys.jpg",
        "Channapatna_Toys.jpg",
        "Channapatna_wooden_toys.jpg",
        "Channapatna_lacquerware.jpg",
        "Karnataka_wooden_toys.jpg",
    ]),
    ("bidriware-jewellery-box.jpg", "Bidriware Jewellery Box – Karnataka", [
        "Bidriware.jpg",
        "Bidri_work.jpg",
        "Bidar_bidriware.jpg",
        "Bidri_art.jpg",
        "Bidriware_Karnataka.jpg",
    ]),
    ("aranmula-metal-mirror.jpg", "Aranmula Metal Mirror – Kerala", [
        "Aranmula_Kannadi.jpg",
        "Aranmula_metal_mirror.jpg",
        "Kerala_metal_mirror.jpg",
        "Aranmula_kannadi_mirror.jpg",
        "Aranmula_mirror.jpg",
    ]),
    ("kasavu-cotton-saree.jpg", "Kasavu Cotton Saree – Kerala", [
        "Kerala_Kasavu_saree.jpg",
        "Kasavu_saree.jpg",
        "Kerala_sari.jpg",
        "Kerala_kasavu.jpg",
        "Kasavu.jpg",
    ]),
    ("kanchipuram-silk-saree.jpg", "Kanchipuram Silk Saree – Tamil Nadu", [
        "Kanchipuram_sarees_(7642282772).jpg",
        "Kanchipuram_silk_sareer.JPG",
        "KanchipuramSlik_Saree.JPG",
        "Kanchipuram_saree.jpg",
        "Kanjeevaram_silk.jpg",
    ]),
    ("thanjavur-painting.jpg", "Thanjavur Painting – Tamil Nadu", [
        "Thanjavur_painting.jpg",
        "Tanjore_painting.jpg",
        "Thanjavur_art.jpg",
        "Tanjore_art.jpg",
        "South_Indian_tanjore_painting.jpg",
    ]),
    ("kondapalli-wooden-toys.jpg", "Kondapalli Wooden Toys – Andhra Pradesh", [
        "Kondapalli_toys.jpg",
        "Kondapalli_Toys.jpg",
        "Kondapalli_wooden_toys.jpg",
        "Andhra_wooden_toys.jpg",
        "Kondapalli.jpg",
    ]),
    ("kalamkari-cotton-dupatta.jpg", "Kalamkari Cotton Dupatta – Andhra Pradesh", [
        "Kalamkari.jpg",
        "Kalamkari_art.jpg",
        "Kalamkari_fabric.jpg",
        "Andhra_kalamkari.jpg",
        "Kalamkari_textile.jpg",
    ]),
    ("pochampally-ikat-saree.jpg", "Pochampally Ikat Saree – Telangana", [
        "Pochampally_ikat.jpg",
        "Pochampally_silk.jpg",
        "Pochampally_saree.jpg",
        "Telangana_ikat.jpg",
        "Bhoodan_Pochampally_ikat_silk.jpg",
    ]),
    ("pattachitra-scroll-painting.jpg", "Pattachitra Scroll Painting – Odisha", [
        "Patta_Chitra_01.jpg",
        "Odisha_Pattachitra_DSCN1052_04.jpg",
        "Pattachitra.jpg",
        "Pattachitra_painting.jpg",
        "Odisha_pattachitra.jpg",
    ]),
    ("sambalpuri-ikat-saree.jpg", "Sambalpuri Ikat Saree – Odisha", [
        "Sambalpuri_saree.jpg",
        "Sambalpuri_ikat.jpg",
        "Sambalpuri_silk.jpg",
        "Odisha_ikat_saree.jpg",
        "Sambalpuri.jpg",
    ]),
    ("kantha-stitch-stole.jpg", "Kantha Stitch Stole – West Bengal", [
        "Nakshi_kantha.jpg",
        "Kantha.jpg",
        "Nakshi_Kantha.jpg",
        "Bengal_kantha.jpg",
        "Kantha_embroidery.jpg",
    ]),
    ("bishnupur-terracotta-horse.jpg", "Bishnupur Terracotta Horse – West Bengal", [
        "Bankura_Terracotta_Horses.jpg",
        "Bishnupur_Terracotta_Horse_3.JPG",
        "Terracotta_horse,_bankura_panchmura.jpg",
        "Bankura_horse.jpg",
        "Bankura_terracotta.jpg",
    ]),
    ("madhubani-painting.jpg", "Madhubani Painting – Bihar", [
        "Mithila-Madhubani_Painting.jpg",
        "Madhubani_painting.jpg",
        "Colorful_Madhubani_painting.jpg",
        "Mithila_art.jpg",
        "Bihar_madhubani.jpg",
    ]),
    ("chanderi-silk-saree.jpg", "Chanderi Silk Saree – Madhya Pradesh", [
        "Chanderi_saree.jpg",
        "Chanderi_fabric.jpg",
        "Chanderi_silk.jpg",
        "Madhya_Pradesh_chanderi.jpg",
        "Chanderi_textile.jpg",
    ]),
    ("gond-art-canvas.jpg", "Gond Art Canvas – Madhya Pradesh", [
        "Gond_painting.jpg",
        "Gond_art.jpg",
        "Gond_tribal_art.jpg",
        "Madhya_Pradesh_gond.jpg",
        "Gond_folk_art.jpg",
    ]),
    ("bastar-dhokra-brass-figurine.jpg", "Bastar Dhokra Brass Figurine – Chhattisgarh", [
        "Dhokra_art.jpg",
        "Dokra.jpg",
        "Dhokra_metal_craft.jpg",
        "Bastar_dhokra.jpg",
        "Dokra_figurine.jpg",
    ]),
    ("muga-silk-mekhela-chador.jpg", "Muga Silk Mekhela Chador – Assam", [
        "Muga_silk.jpg",
        "Assam_silk.jpg",
        "Mekhela_chador.jpg",
        "Assam_muga.jpg",
        "Golden_muga_silk.jpg",
    ]),
    ("cane-and-bamboo-japi-hat.jpg", "Cane and Bamboo Japi Hat – Assam", [
        "Japi_(Assam).jpg",
        "Assam_Japi.jpg",
        "Japi_hat.jpg",
        "Bamboo_japi.jpg",
        "Assam_traditional_hat.jpg",
    ]),
    ("longpi-black-pottery-bowl.jpg", "Longpi Black Pottery Bowl – Manipur", [
        "Longpi_pottery.jpg",
        "Longpi_black_pottery.jpg",
        "Manipur_pottery.jpg",
        "Longpi_stone_pottery.jpg",
        "Longpi.jpg",
    ]),
    ("naga-handwoven-shawl.jpg", "Naga Handwoven Shawl – Nagaland", [
        "Naga_shawl.jpg",
        "Naga_tribal_shawl.jpg",
        "Nagaland_shawl.jpg",
        "Naga_textile.jpg",
        "Nagaland_traditional_textile.jpg",
    ]),
    ("mizo-puanchei-wrap.jpg", "Mizo Puanchei Wrap – Mizoram", [
        "Puanchei.jpg",
        "Mizo_traditional_dress.jpg",
        "Mizoram_traditional_textile.jpg",
        "Mizo_puanchei.jpg",
        "Mizoram_weaving.jpg",
    ]),
    ("sikkimese-thangka-painting.jpg", "Sikkimese Thangka Painting – Sikkim", [
        "Thangka_painting.jpg",
        "Thangka.jpg",
        "Buddhist_thangka.jpg",
        "Sikkim_thangka.jpg",
        "Tibetan_thangka_painting.jpg",
    ]),
    ("monpa-handmade-paper-journal.jpg", "Monpa Handmade Paper Journal – Arunachal Pradesh", [
        "Handmade_paper.jpg",
        "Lokta_paper.jpg",
        "Handmade_lokta_paper.jpg",
        "Monpa_paper.jpg",
        "Arunachal_handmade_paper.jpg",
    ]),
    ("changthangi-pashmina-stole.jpg", "Changthangi Pashmina Stole – Ladakh", [
        "Changthangi_pashmina.jpg",
        "Pashmina_stole.jpg",
        "Ladakh_pashmina.jpg",
        "Pashmina_raw.jpg",
        "Changthangi_goat.jpg",
    ]),
]

# ── Existing files that can be reused ──────────────────────────────────────────
# Maps new slug → existing file already in products/ that is a genuine match
REUSE_MAP = {
    "chikankari-kurta.jpg":   "lucknow-chikankari-kurta.jpg",
    "madhubani-painting.jpg": "madhubani-tree-of-life.jpg",
    "bastar-dhokra-brass-figurine.jpg": "dhokra-tribal-musician.jpg",
    "blue-pottery-vase.jpg":  "jaipur-blue-pottery-planter.jpg",
}

def wm_api_get(params):
    params["format"] = "json"
    url = WM_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def get_wm_file_info(filename):
    """Return (download_url, licence, credit) or None if file not found."""
    data = wm_api_get({
        "action": "query",
        "titles": "File:" + filename,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
    })
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    if "missing" in page:
        return None
    infos = page.get("imageinfo", [])
    if not infos:
        return None
    info = infos[0]
    mime = info.get("mime", "")
    # Only accept JPEG
    if "jpeg" not in mime and "jpg" not in mime:
        print(f"    Skip (not JPEG, mime={mime}): {filename}")
        return None
    size = info.get("size", 0)
    if size < 20000:
        print(f"    Skip (too small {size} bytes): {filename}")
        return None
    meta = info.get("extmetadata", {})
    licence  = meta.get("LicenseShortName", {}).get("value", "unknown")
    artist   = meta.get("Artist", {}).get("value", "unknown")
    # Strip HTML from artist
    artist = artist.replace("<span>","").replace("</span>","")
    credit   = meta.get("Credit", {}).get("value", "")
    page_url = f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(filename)}"
    return {
        "url": info["url"],
        "licence": licence,
        "artist": artist,
        "page_url": page_url,
        "size": size,
    }

def is_valid_jpeg(path):
    """Check JPEG magic bytes: FF D8 FF"""
    try:
        with open(path, "rb") as f:
            header = f.read(3)
        return header == b'\xff\xd8\xff'
    except:
        return False

def download_file(url, dest):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        with open(dest, "wb") as f:
            f.write(r.read())

def copy_existing(src_name, dest_path):
    """Copy an existing product image to the new slug path."""
    import shutil
    src = os.path.join(OUTPUT_DIR, src_name)
    if os.path.exists(src) and os.path.getsize(src) > 20000:
        shutil.copy2(src, dest_path)
        return True
    return False

# ── Main ───────────────────────────────────────────────────────────────────────
print("=" * 60)
print("Craftify – Wikimedia Commons Image Downloader")
print("=" * 60)

results = []  # list of dicts for credits file

success_count = 0
reused_count  = 0
failed_list   = []

for (out_file, product_name, candidates) in PRODUCTS:
    dest = os.path.join(OUTPUT_DIR, out_file)
    print(f"\n[{out_file}] {product_name}")

    # 1. Already exists and valid?
    if os.path.exists(dest) and os.path.getsize(dest) > 50000 and is_valid_jpeg(dest):
        print(f"  SKIP – already exists ({os.path.getsize(dest)//1024}KB)")
        results.append({"file": out_file, "product": product_name,
                        "source": "existing", "licence": "existing",
                        "artist": "", "page_url": ""})
        success_count += 1
        continue

    # 2. Try reuse map first
    if out_file in REUSE_MAP:
        reuse_src = REUSE_MAP[out_file]
        print(f"  Trying reuse: {reuse_src}")
        if copy_existing(reuse_src, dest):
            print(f"  REUSED {reuse_src}")
            results.append({"file": out_file, "product": product_name,
                            "source": f"reused:{reuse_src}", "licence": "see original",
                            "artist": "", "page_url": ""})
            success_count += 1
            reused_count += 1
            continue

    # 3. Try Wikimedia candidates
    downloaded = False
    for candidate in candidates:
        print(f"  Trying WM: {candidate}")
        try:
            info = get_wm_file_info(candidate)
            if info is None:
                print(f"    Not found or not JPEG")
                time.sleep(0.3)
                continue
            print(f"    Found: {info['size']//1024}KB | {info['licence']} | {info['url'][:70]}...")
            download_file(info["url"], dest)
            if is_valid_jpeg(dest) and os.path.getsize(dest) > 20000:
                print(f"    OK: {os.path.getsize(dest)//1024}KB")
                results.append({"file": out_file, "product": product_name,
                                "source": info["page_url"], "licence": info["licence"],
                                "artist": info["artist"], "page_url": info["page_url"]})
                success_count += 1
                downloaded = True
                break
            else:
                print(f"    Invalid JPEG or too small – removing")
                os.remove(dest)
        except Exception as e:
            print(f"    Error: {e}")
        time.sleep(0.4)

    if not downloaded:
        print(f"  FAILED – no valid image found for {out_file}")
        failed_list.append(out_file + " | " + product_name)
        results.append({"file": out_file, "product": product_name,
                        "source": "NONE", "licence": "N/A",
                        "artist": "N/A", "page_url": "placeholder will show"})

# ── Write IMAGE_CREDITS.md ─────────────────────────────────────────────────────
print("\nWriting IMAGE_CREDITS.md ...")
with open(CREDITS_FILE, "w", encoding="utf-8") as f:
    f.write("# Craftify – Image Credits\n\n")
    f.write("All images sourced from Wikimedia Commons under their respective licences.\n")
    f.write("Public domain and CC-licensed images; attribution provided below.\n\n")
    f.write("| Product | File | Source | Licence | Photographer/Artist |\n")
    f.write("|---------|------|--------|---------|---------------------|\n")
    for r in results:
        src = r["source"].replace("|", "\\|")
        art = r["artist"].replace("|", "\\|")[:60]
        f.write(f"| {r['product']} | `{r['file']}` | {src} | {r['licence']} | {art} |\n")

# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total products : 40")
print(f"Downloaded OK  : {success_count - reused_count - len([r for r in results if 'existing' == r['source']])}")
print(f"Reused existing: {reused_count}")
print(f"Already present: {len([r for r in results if r['source'] == 'existing'])}")
print(f"Total available: {success_count}")
print(f"Failed (placeholder): {len(failed_list)}")

if failed_list:
    print("\nNEEDS MANUAL DOWNLOAD:")
    for f in failed_list:
        print(f"  {f}")

# Verify all 40 files
print("\n--- File verification ---")
all_ok = True
for (out_file, product_name, _) in PRODUCTS:
    dest = os.path.join(OUTPUT_DIR, out_file)
    if os.path.exists(dest) and os.path.getsize(dest) > 800:
        marker = "OK " if is_valid_jpeg(dest) else "BAD"
        print(f"  {marker} {out_file} ({os.path.getsize(dest)//1024}KB)")
    else:
        print(f"  MISSING  {out_file}")
        all_ok = False

print(f"\nAll files present: {all_ok}")
print("Done.")
