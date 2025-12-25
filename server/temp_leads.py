"""
Docstring for server.temp_leads
Creates inside TEMP_PATH (default: ./__temp__/) folders for each lead created.

"""
from os import mkdir, listdir
from shutil import rmtree

import sys

sys.path.insert(1, '../')

from config import TEMP_PATH

from log import log
from lead import Lead



def create(leads: list[Lead]) -> bool:
    log("Attempting to create temp folders for given leads...")
    success: bool = True
    for lead in leads:
        try:
            mkdir(f"{TEMP_PATH}/{str(lead.id)}")
        except Exception as e:
            success = False
    return success


def wipe_all() -> None:
    ls=listdir(TEMP_PATH)
    print(ls)
    for dir in ls:
        rmtree(TEMP_PATH+"/"+str(dir))



def test_1():
    log("="*50)
    log("TESTING SCRIPT")
    lead_list=[
        Lead(150,"Al-74", "0797556550", "Via caccolemontate 15", "Lugano", "aa", [], 4),
        Lead(2,"Al-74", "0797556550", "Via caccolemontate 15", "Lugano", "aa", [], 4),
    ]
    create(lead_list)


def test_2():
    wipe_all()

if __name__ == "__main__":
    test_1()
