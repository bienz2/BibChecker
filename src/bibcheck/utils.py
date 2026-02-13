import json
import re
import unicodedata
import string
import os
import html
from pathlib import Path

SPECIAL_LETTER_MAP = str.maketrans({
    "ı": "i", "İ": "I",
    # add more if you want:
    "ß": "ss", "Ø": "O", "ø": "o", "Æ": "AE", "æ": "ae",
    "Œ": "OE", "œ": "oe", "Ł": "L", "ł": "l",
})

NAME_SUFFIXES = {
    "jr", "sr", "ii", "iii", "iv", "v", "vi"
}

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load exclusions file {path}: {e}")
        return {}

def load_source_patterns(extra_files=None):
    package_dir = Path(__file__).resolve().parent
    default_path = package_dir / "exclusions.json"

    exclusions = load_json(default_path)

    # User-provided extra files (list of paths)
    for path in extra_files or []:
        user_excl = load_json(path)
        exclusions.update(user_excl)

    return exclusions

exclusions = load_source_patterns()


def remove_special_chars(s):
    if not s:
        return

    s = html.unescape(s) 
    s = re.sub(r'<mml:[^>]+>', '', s)
    s = re.sub(r'</mml:[^>]+>', '', s)
    s = re.sub(r'<[^>]+>', '', s)    
    s = s.translate(SPECIAL_LETTER_MAP)    
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r'[\u2010-\u2015\u2212]', '-', s)    
    s = re.sub(r'\b([A-Z][a-z]+)\s+([a-z])\b', r'\1\2', s)
    
    return s

def format_for_url(text):
    text = text.lower()
    text = text.replace('\n', '').replace(' ', '')
    return text

def normalize_title(title):
    if not title:
        return title

    title = remove_special_chars(title)
    title = title.replace("’", "").replace("'", "")
    title = re.sub(r'\s+', ' ', title)
    title = title.replace('- ', '')
    title = title.replace('/', ' ')
    title = re.sub(r"[^a-zA-Z0-9_]+", " ", title)
    title = re.sub(r"\s+", " ", title)
    return title.lower().strip() 

def normalize_title_concat(title):
    if not title:
        return title

    title = remove_special_chars(title)
    title = title.replace("’", "").replace("'", "")
    title = re.sub(r'\s+', ' ', title)
    title = title.replace('/', ' ')
    title = re.sub(r"[^a-zA-Z0-9_]+", " ", title)
    title = re.sub(r"\s+", " ", title)
    return title.lower().strip() 

def normalize_authors(author_block):
    if not author_block:
        return author_block

    cleaned = remove_special_chars(author_block).replace('  ', ' ')
    cleaned = cleaned.replace('- ', '-')
    cleaned = re.sub(r"[^a-zA-Z,.\s]+", "", cleaned)
    return cleaned

def normalize_last_name(name, last_first = False):
    name = name.strip()

    if last_first:
        last = name.split(",", 1)[0]
        return last.strip().lower()

    parts = name.lower().split()
    parts = [p.strip(" .") for p in parts]
    while parts and parts[-1] in NAME_SUFFIXES:
        parts.pop()

    if parts:
        return parts[-1]

    return "" 

def extract_last_names(raw, from_list=False, last_first=False):
    if not raw:
        return

    names = []
    et_al_index = -1

    if from_list:
        iterable = [normalize_authors(a) for a in raw if a]
    else:
        cleaned = normalize_authors(raw)
        if not cleaned:
            return None, -1 
    
        if last_first:
            iterable = re.split(
                r',\s*(?=[A-Z][a-zA-Z\-]*(?:\s+[A-Z][a-zA-Z\-]*)*,)',
                cleaned
            )
        else:
            iterable = re.split(
                r',\s+and\s+|\s+and\s+|,\s*',
                cleaned
            )

    for name in iterable:
        name = name.strip()
        if not name:
            continue

        has_et_al = "et al" in name.lower()
        if has_et_al:
            name = re.sub(r'\bet\s+al\.?\b', '', name, flags=re.I).strip(" .\n")

        if name:
            names.append(normalize_last_name(name, last_first))

        if has_et_al:
            et_al_index = len(names)
            return names, et_al_index

    return names, et_al_index

def replace_et_al(authors0, authors1, last_first = False):
    list0 = [] 
    list1 = []

    if authors0:
        list0, et_al0 = extract_last_names(authors0, False, last_first)
    if authors1:
        list1, et_al1 = extract_last_names(authors1, True, False)

    if list0 and list1:        
        if et_al0 >= 0 and et_al1 < 0:
            list1 = list1[:et_al0]
        elif et_al1 >= 0 and et_al0 < 0:
            list0 = list0[:et_al1]
        elif et_al0 < et_al1:
            list1 = list1[:et_al0]
        elif et_al1 < et_al0:
            list0 = list0[:et_al1]

    return list0, list1


