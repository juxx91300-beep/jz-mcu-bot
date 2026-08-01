#!/usr/bin/env python3
"""
JZ MCU — YouTube -> Discord notifier
--------------------------------------
Verifie les flux RSS YouTube des createurs listes ci-dessous et poste
automatiquement les nouvelles videos dans un salon Discord via un webhook.

Aucune cle API YouTube n'est necessaire : on utilise le flux RSS public
de YouTube (https://www.youtube.com/feeds/videos.xml?channel_id=...).

Le webhook Discord est lu depuis la variable d'environnement
DISCORD_WEBHOOK_URL (ne jamais l'ecrire en dur dans ce fichier).
"""

import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

# ── Createurs a suivre : nom affiche -> ID de chaine YouTube ──
# Pour ajouter/retirer un createur, edite juste ce dictionnaire.
CREATORS = {
    "Iro Sef": "UCLz6B7LxOdwgHbcgFi_hpQQ",
    "Kevin Bukkart": "UCnUiNjxobt87xkhf9Fo7_Dw",
}

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()

ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def fetch_latest_video(channel_id):
    """Renvoie (video_id, title, url, thumbnail, published) de la derniere
    video publiee sur la chaine, ou None si le flux est vide/inaccessible."""
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0 (JZ-MCU-Bot)"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
    except Exception as e:
        print(f"[WARN] Impossible de recuperer le flux pour {channel_id}: {e}", file=sys.stderr)
        return None

    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        print(f"[WARN] Flux XML invalide pour {channel_id}: {e}", file=sys.stderr)
        return None

    entry = root.find("atom:entry", ATOM_NS)
    if entry is None:
        return None

    video_id_el = entry.find("yt:videoId", ATOM_NS)
    title_el = entry.find("atom:title", ATOM_NS)
    link_el = entry.find("atom:link", ATOM_NS)
    published_el = entry.find("atom:published", ATOM_NS)
    thumb_el = entry.find("media:group/media:thumbnail", ATOM_NS)

    video_id = video_id_el.text if video_id_el is not None else None
    title = title_el.text if title_el is not None else "Nouvelle video"
    url = link_el.get("href") if link_el is not None else f"https://www.youtube.com/watch?v={video_id}"
    published = published_el.text if published_el is not None else ""
    thumbnail = thumb_el.get("url") if thumb_el is not None else None

    if not video_id:
        return None

    return {
        "video_id": video_id,
        "title": title,
        "url": url,
        "thumbnail": thumbnail,
        "published": published,
    }


def post_to_discord(creator_name, video):
    if not DISCORD_WEBHOOK_URL:
        print("[ERREUR] DISCORD_WEBHOOK_URL n'est pas defini. Rien n'est poste.", file=sys.stderr)
        return False

    embed = {
        "title": video["title"],
        "url": video["url"],
        "description": f"Nouvelle video de **{creator_name}** !",
        "color": 0x8C82F0,  # violet JZ
        "timestamp": video["published"] or None,
        "footer": {"text": "JZ MCU • YouTube"},
    }
    if video.get("thumbnail"):
        embed["image"] = {"url": video["thumbnail"]}

    payload = {
        "username": "JZ MCU",
        "content": f"📺 **{creator_name}** vient de sortir une nouvelle video !\n{video['url']}",
        "embeds": [embed],
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (JZ-MCU-Bot)"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            resp.read()
        print(f"[OK] Poste sur Discord : {creator_name} -> {video['title']}")
        return True
    except Exception as e:
        print(f"[ERREUR] Envoi Discord echoue pour {creator_name}: {e}", file=sys.stderr)
        return False


def main():
    state = load_state()
    changed = False

    for creator_name, channel_id in CREATORS.items():
        video = fetch_latest_video(channel_id)
        if not video:
            continue

        last_seen = state.get(channel_id)

        if last_seen is None:
            # Premiere execution pour cette chaine : on memorise la derniere
            # video existante SANS la poster, pour ne pas spammer d'anciennes
            # videos des la mise en place du bot.
            state[channel_id] = video["video_id"]
            changed = True
            print(f"[INIT] {creator_name}: derniere video memorisee ({video['video_id']}), pas de post.")
            continue

        if last_seen != video["video_id"]:
            ok = post_to_discord(creator_name, video)
            if ok:
                state[channel_id] = video["video_id"]
                changed = True
        else:
            print(f"[--] {creator_name}: rien de nouveau.")

    if changed:
        save_state(state)


if __name__ == "__main__":
    main()
