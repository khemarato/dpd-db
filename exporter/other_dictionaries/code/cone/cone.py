import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
from tools.goldendict_exporter import export_to_goldendict_with_pyglossary
from tools.goldendict_exporter import DictEntry, DictInfo, DictVariables
from tools.printer import p_green, p_title, p_yes
from tools.tic_toc import tic, toc

def main():
    tic()
    p_title("exporting cone")
    with open ("exporter/other_dictionaries/code/cone/source/cone_dict.json") as f:
        cone_dict = json.load(f)
    
    p_green("making dict data")
    dict_data = []
    for key, html_body in cone_dict.items():

        html_body = html_body.replace(" — ", "")

        if "href" in html_body:
            html_body = remove_links(html_body)
        
        if html_body:
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <link href="cone.css" rel="stylesheet">
            </head>
            <body> 
            """
            html += html_body
            html += "</body></html>"

            dict_entry = DictEntry(
                word=key,
                definition_html=html,
                definition_plain="",
                synonyms=make_synonyms_list(key),
            )
            dict_data.append(dict_entry)
    
    dict_info = DictInfo(
        bookname="Cone Test",
        author="Margaret Cone",
        description="",
        website="",
        source_lang="pi",
        target_lang="en",
    )

    dict_var = DictVariables(
        css_path=Path("exporter/other_dictionaries/code/cone/source/cone.css"),
        js_path=None,
        output_path=Path("exporter/other_dictionaries/code/cone"),
        dict_name="Dictionary of Pāli by Margaret Cone",
        icon_path=None
    )
    p_yes("")

    export_to_goldendict_with_pyglossary(
        dict_info,
        dict_var,
        dict_data,
        zip_synonyms=False
    )

    toc()
            
def make_synonyms_list(word):
    synonyms = set()
    
    if re.findall(r"\d", word):
        word = re.sub(r"\d", "", word)
    
    if re.findall(r"ar$", word):
        word_ā = re.sub(r"ar$", "ā", word)
        synonyms.add(word_ā)

    if re.findall(r"in$", word):
        word_ī = re.sub(r"in$", "ī", word)
        synonyms.add(word_ī)
        word_i = re.sub(r"in$", "i", word)
        synonyms.add(word_i)
    
    if "(" in word:
        word = re.sub(r"\(|\)", "", word)
    
    synonyms.add(word)
    return list(synonyms)


def remove_links(html):
    # return html
    soup = BeautifulSoup(html, 'lxml')
    for a in soup.find_all('a'):
        span = soup.new_tag('span', style='color: blue;')
        if a.string: 
            span.string = a.string
        a.replace_with(span)
    return str(soup)


if __name__ == "__main__":
    main()