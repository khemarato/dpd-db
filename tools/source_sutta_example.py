import re
import time

from bs4 import BeautifulSoup
from nltk import sent_tokenize
from typing import Tuple, List

from tools.paths import ProjectPaths
from tools.pali_text_files import cst_texts


def make_cst_soup(
        pth: ProjectPaths,
        book,
        unwrap_notes=True
):
    filename = ""

    if book in cst_texts:
        filename = cst_texts[book][0].replace(".txt", ".xml")

        with open(
            pth.cst_xml_roman_dir.joinpath(filename),
            "r", encoding="UTF-16") as f:
            xml = f.read()

        # FIXME delete transliterate roman dir everywhere
        # it's already transliterated!

        soup = BeautifulSoup(xml, "xml")

        # remove all the "pb" tags
        pbs = soup.find_all("pb")
        for pb in pbs:
            pb.decompose()

        if unwrap_notes:
            # unwrap all the notes (variant readings)
            notes = soup.find_all("note")
            for note in notes:
                note.replace_with(fr" [{note.text}] ")

        # unwrap all the hi parunum dot tags (paragraphy numbers)
        his = soup.find_all("hi", rend=["paranum", "dot"])
        for hi in his:
            hi.unwrap()

        return soup
    
    else:
        return BeautifulSoup("")
    


def find_source_sutta_example(
        pth: ProjectPaths,
        book: str, 
        text_to_find: str
        ) -> List[Tuple[str, str, str]]:

    sutta_examples: List[Tuple[str, str, str]] = []

    soup = make_cst_soup(pth, book) 

    ps = soup.find_all("p")
    source = ""
    sutta = ""

    sutta_counter = 0
    kn_counter = 0
    four_nikayas = [
        "dn1", "dn2", "dn3",
        "mn1", "mn2", "mn3",
        "sn1", "sn2", "sn3", "sn4", "sn5",
        "an1", "an2", "an3", "an4", "an5",
        "an6", "an7", "an8", "an9", "an10", "an11"]
    
    for p in ps:
        if book in four_nikayas:
            if p["rend"] == "subhead":
                if "suttaṃ" in p.text:
                    sutta_counter += 1
                source = book.upper()
                book_name = re.sub(r"\d", "", source)
                # add space to digtis
                # source = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", source)
                sutta_number = ""
                try:
                    sutta_number = p.next_sibling.next_sibling["n"]
                except Exception as e:
                    print(e)
                    print(text_to_find)
                    print(p)
                    continue

                # choose which method to number suttas according to book
                if book.startswith("mn1"):
                    source = f"{book_name}{sutta_counter}"
                elif book.startswith("mn2"):
                    source = f"{book_name}{sutta_counter+50}"
                elif book.startswith("mn3"):
                    source = f"{book_name}{sutta_counter+100}"
                elif book.startswith("an"):
                    source = f"{source}.{sutta_number}"
                elif book.startswith("sn"):
                    source = ""
                # FIXME system for Saṃyutta Nikāya

                # remove the digits and the dot in sutta name
                sutta = re.sub(r"\d*\. ", "", p.text)
                sutta = re.sub(r" \[.*?\]", "", sutta)
            
        # vin3 vin4 mahāvagga & culavagga
        if (
            book == "vin3"
            or book == "vin4"
        ):
            if book == "vin3":
                book_name = "VIN3"
            else:
                book_name = "VIN4"

            if p.has_attr("rend") and p["rend"] == "subhead":
                subhead = p.text.lower()

                bad_subheadings = [
                    "soṇassa pabbajjā", "abhiññātānaṃ pabbajjā"]
                if subhead in bad_subheadings:
                    continue

                # remove / keep digits 
                sub_num = re.sub("\\. *.+", "", subhead)
                sub_title = re.sub("\\d*\\. *", "", subhead)

                # if subnum not a digit, then remove
                if not sub_num[0].isnumeric():
                    sub_num = ""
                
                # find the previous head + chapter
                chapter_head = p.find_previous("head", attrs={"rend": "chapter"}).text
                
                # remove / keep digits
                chapter_num = re.sub("\\. *.+", ".", chapter_head)
                chapter_title =  re.sub("\\d*\\. *", "", chapter_head)

                # construct the source if there's valid parts
                # if not, the previous source will be used
                if book_name and chapter_num and sub_num:
                    source = f"{book_name}.{chapter_num}{sub_num}"
                    print(source, end=" ")

                # construct the sutta name
                sutta = f"{chapter_title}, {sub_title}"
                sutta = sutta.lower()
                print(sutta)

        # dn
        if "dn" in book:
            book_name = "DN"
            if p.has_attr("rend") and p["rend"] == "subhead":
                # Find the previous "head" tag with "rend" attribute containing "chapter"
                chapter_head = p.find_previous("head", attrs={"rend": "chapter"})
                chapter_text = chapter_head.text
                pattern = r"^(\d+)\.\s+(.*)$"
                match = re.match(pattern, chapter_text)
                if match:
                    if book == "dn1":
                        source = f"{book_name}{match.group(1)}"
                    if book == "dn2":
                        # there are 13 suttas previously in dn1
                        source = f"{book_name}{int(match.group(1))+13}"
                    if book == "dn3":
                        # there are 13+10 suttas previously in dn1 & dn2
                        source = f"{book_name}{int(match.group(1))+23}"
                    sutta = match.group(2)

        # kn1
        if book == "kn1":
            book_name = "KHP"
            chapter_text = None
            if not chapter_text:
                chapter_div = p.find_parent("div", {"type": "chapter"})
                if chapter_div:
                    chapter_text = chapter_div.find("head").get_text()
                    pattern = r"^(\d+)\.\s+(.*)$"
                    match = re.match(pattern, chapter_text)
                    if match:
                        source = f"{book_name}{match.group(1)}"
                        sutta = match.group(2)
                    

        # kn2
        elif book == "kn2":
            book_name = "DHP"
            if p.has_attr("rend") and p["rend"] == "hangnum":
                # Find the previous "head" tag with "rend" attribute containing "chapter"
                chapter_head = p.find_previous("head", attrs={"rend": "chapter"})
                if chapter_head is not None:
                    chapter_text = chapter_head.string.strip()
                    pattern = r"^(\d+)\.\s+(.*)$"
                    match = re.match(pattern, chapter_text)
                    if match:
                        source = f"{book_name}{match.group(1)}"
                        sutta = match.group(2)


        elif book == "kn3":
            book_name = "UD"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn4":
            book_name = "ITI"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn5":
            book_name = "SNP"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn6":
            book_name = "VV"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn7":
            book_name = "PV"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn8":
            book_name = "TH"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn9":
            book_name = "THI"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn10":
            book_name = "APA"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn11":
            book_name = "API"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub("\\d*\\. *", "", p.text)

        elif book == "kn12":
            book_name = "BV"
            if p.has_attr("rend") and p["rend"] == "hangnum":
                # Find the previous "head" tag with "rend" attribute containing "chapter"
                chapter_head = p.find_previous("head", attrs={"rend": "chapter"})
                if chapter_head is not None:
                    chapter_text = chapter_head.string.strip()
                    pattern = r"^(\d+)\.\s+(.*)$"
                    match = re.match(pattern, chapter_text)
                    if match:
                        source = f"{book_name}{match.group(1)}"
                        sutta = match.group(2)


        elif book == "kn13":
            book_name = "CP"
            if p.has_attr("rend") and p["rend"] == "hangnum":
                # Find the previous "head" tag with "rend" attribute containing "chapter"
                chapter_head = p.find_previous("head", attrs={"rend": "chapter"})
                if chapter_head is not None:
                    chapter_text = chapter_head.string.strip()
                    pattern = r"^(\d+)\.\s+(.*)$"
                    match = re.match(pattern, chapter_text)
                    if match:
                        source = f"{book_name}{match.group(1)}"
                        sutta = match.group(2)

        elif book == "kn14":
            book_name = "JA"
            if p["rend"] == "subhead":
                kn_counter += 1
                source = f"{book_name}{kn_counter}"
                sutta = re.sub(" .*$", "", sutta)

        elif book == "kn15":
            book_name = "NIDD1"
            if p.has_attr("rend") and p["rend"] == "hangnum":
                # Find the previous "head" tag with "rend" attribute containing "chapter"
                chapter_head = p.find_previous("head", attrs={"rend": "chapter"})
                if chapter_head is not None:
                    chapter_text = chapter_head.string.strip()
                    pattern = r"^(\d+)\.\s+(.*)$"
                    match = re.match(pattern, chapter_text)
                    if match:
                        source = f"{book_name}.{match.group(1)}"
                        sutta = match.group(2)


        elif book == "kn16":
            book_name = "NIDD2"
            if p["rend"] == "subhead":
                kn_counter += 1
                # 1-20 is the original pārayan verses and khaggavisāṇa
                # 21-37 is the cūḷaniddesa
                # 38-41 is the commentary on khaggavisāṇa
                if kn_counter < 21:
                    source = f"{book_name}.{kn_counter}"
                    sutta = re.sub(" .*$", "", sutta)
                    print(f"{kn_counter} 1 {source:<10}{sutta:<10}")
                elif 21 <= kn_counter < 38:
                    source = f"{book_name}.{kn_counter-20}"
                    sutta = re.sub(" .*$", "", sutta)
                    print(f"{kn_counter} 1 {source:<10}{sutta:<10}")
                elif kn_counter >=38:
                    source = f"{book_name}.19"
                    sutta = "Khaggavisāṇasuttaniddeso, " + re.sub(" .*$", "", sutta)
                    print(f"{kn_counter} 1 {source:<10}{sutta:<10}")


        text = clean_example(p.text)

        if text_to_find is not None and re.findall(text_to_find, text):

            # compile gathas line by line
            if "gatha" in p["rend"]:
                example = ""

                start_time = time.time()
                while True:
                    if p.text == "\n":
                        p = p.previous_sibling
                    elif p["rend"] == "gatha1":
                        break
                    elif p["rend"] == "gatha2":
                        p = p.previous_sibling
                    elif p["rend"] == "gatha3":
                        p = p.previous_sibling
                    elif p["rend"] == "gathalast":
                        p = p.previous_sibling
                    if time.time() - start_time > 1:
                        print(f"[bright_red]{text_to_find} [red]is stuck in a loop")
                        break

                text = clean_gatha(p.text)
                # text = text.replace(".", ",\n")
                example += text

                while True:
                    try:
                        if p is not None:
                            p = p.next_sibling
                            if p.text == "\n":
                                pass
                            elif p["rend"] == "gatha2":
                                text = clean_gatha(p.text)
                                text = text.replace(".", ",")
                                example += text
                            elif p["rend"] == "gatha3":
                                text = clean_gatha(p.text)
                                text = text.replace(".", ",")
                                example += text
                            elif p["rend"] == "gathalast":
                                text = clean_gatha(p.text)
                                text = re.sub(",$", ".", text)
                                example += text
                                break
                        else:
                            break
                    except AttributeError as e:
                        print(f"[red]{e}")
                        print(text_to_find)
                        print(p)
                        break
                
                sutta_examples += [(source, sutta.lower(), example)]

            # or compile sentences
            else:
                sentences = sent_tokenize(text)
                for i, sentence in enumerate(sentences):
                    if re.findall(text_to_find, sentence):
                        prev_sentence = sentences[i - 1] if i > 0 else ""
                        next_sentence = sentences[i + 1] if i < len(sentences)-1 else ""
                        sutta_examples += [(
                            source,
                            sutta.lower(),
                            f"{prev_sentence} {sentence} {next_sentence}")]

    return sutta_examples


# FIXME remove clean_example from functions
def clean_example(text):
    text = text.strip()
    text = text.lower()
    text = text.replace("‘", "")
    text = text.replace(" – ", ", ")
    text = text.replace("’", "")
    text = text.replace("…pe॰…", " ... ")
    text = text.replace(";", ",")
    text = text.replace("  ", " ")
    text = text.replace("..", ".")
    text = text.replace(" ,", ",")
    
    # remove abbreviations in brackets, no more than 20 characters
    text = re.sub(r" \([^)]{0,20}\.\)", "", text)
    
    return text

# FIXME remove clean_gatha from functions
def clean_gatha(text):
    text = clean_example(text)
    text = text.strip()
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace(", ", ",\n")
    text = re.sub(",$", ",\n", text)
    return text


if __name__ == "__main__":
    pth = ProjectPaths()
    book = "mn3"
    text_to_find = "santi"
    sutta_examples = find_source_sutta_example(pth, book, text_to_find)
    for sutta_example in sutta_examples:
        print(sutta_example)
        input()