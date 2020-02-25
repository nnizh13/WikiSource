import glob
from typing import (List, Dict, Tuple, Any)
from tqdm import tqdm
import os
import subprocess


def call_wc(fname:str, choice: str = 'word'):
    """
    choice: one of ['word', 'char']
    """
    p = subprocess.Popen(['wc', fname], stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)

    if choice == 'word':
        return int(result.strip().split()[0])
    elif choice == 'char':
        return int(result.strip().split()[1])


def count_by_year(root_dir: str = '*/', choice: str = 'word'):
    year_folders = glob.glob(root_dir)

    year_to_count: Dict[str, Tuple[int, int]] = {}
    for year in tqdm(year_folders, ncols=100):
        articles = glob.glob(os.path.join(year, '*'))
        art_count = len(articles)

        token_count = 0
        for article in articles:
            token_count += call_wc(article, choice)
        
        year_short = os.path.basename(year)
        year_to_count[year_short] = (art_count, token_count)

    return year_to_count