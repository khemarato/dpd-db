"""A few helpful lists and functions for the exporter."""

from typing import Dict, List, Set, Optional

from sqlalchemy.orm import Session

from db.get_db_session import get_db_session
from db.models import PaliWord
from tools.paths import ProjectPaths

_cached_cf_set: Optional[Set[str]] = None

def cf_set_gen(pth: ProjectPaths) -> Set[str]:
    """generate a list of all compounds families"""
    global _cached_cf_set

    if _cached_cf_set is not None:
        return _cached_cf_set

    db_session = get_db_session(pth.dpd_db_path)
    cf_db = db_session.query(
        PaliWord
    ).filter(PaliWord.family_compound != ""
             ).all()

    cf_set: Set[str] = set()
    for i in cf_db:
        if i.family_compound is None:
            continue
        cfs: List[str] = i.family_compound.split(" ")
        for cf in cfs:
            cf_set.add(cf)

    _cached_cf_set = cf_set
    return cf_set


def make_roots_count_dict(db_session: Session) -> Dict[str, int]:
    roots_db = db_session.query(PaliWord).all()
    roots_count_dict: Dict[str, int] = dict()
    for i in roots_db:
        if i.root_key is None:
            continue
        if i.root_key in roots_count_dict:
            roots_count_dict[i.root_key] += 1
        else:
            roots_count_dict[i.root_key] = 1

    return roots_count_dict
