#!/usr/bin/env python3

"""Find the most common root familes"""

import pyperclip

from collections import Counter
from rich import print

from db.get_db_session import get_db_session
from db.models import DpdHeadwords
from tools.paths import ProjectPaths


def main():
    pth = ProjectPaths()
    db_session = get_db_session(pth.dpd_db_path)
    db = db_session.query(DpdHeadwords).all()

    root_family_dict = {}
    for counter, i in enumerate(db):
        if (
            i.root_key
            and i.family_root
            and "[" not in i.sanskrit
        ):  
            if i.root_key not in root_family_dict:
                root_family_dict[i.root_key] = 1
            else:
                root_family_dict[i.root_key] += 1

    counter = Counter(root_family_dict)

    # Print the most common values
    for key, count in counter.most_common():
        print(key, count)
        pyperclip.copy(key)
        route = input()
        if route == "x":
            return

if __name__ == "__main__":
    main()

# upto √ñā 553
