import configparser
import logging
import os
import time
#import argparse
#import sys


#File definitions
EXE = "h3hota HD.exe"
DAT = "HotA.dat"
MPD = "h3hota_maped.exe"


HEX = {
    "RefuseLevelUp": {
        True: [(EXE, 0x0F9BA4, b"\xEB")],
        False: [(EXE, 0x0F9BA4, b"\x74")],
    },
    "DispelOnEnemiesOnly": {
        True: [(EXE, 0x1A8477, b'\x8B\x55\x0C\x8B\x8F\xF4\x00\x00\x00\x39\xD1\x0F\x85\xB9\x00\x00\x00\xEB\x69')],
        False: [(EXE, 0x1A8477, b'\x8B\x8E\xC0\x53\x00\x00\x51\x8B\x4D\xFC\x6A\x23\xE8\x68\xCE\xF3\xFF\x83\xF8')],
    },
    "MaximumLuck4": {
        True: [
            (EXE, 0x03F658, b"\x04"),
            (EXE, 0x03F65F, b"\x04"),
            (EXE, 0x04153A, b"\x04"),
            (EXE, 0x041541, b"\x04"),
        ],
        False: [
            (EXE, 0x03F658, b"\x03"),
            (EXE, 0x03F65F, b"\x03"),
            (EXE, 0x04153A, b"\x03"),
            (EXE, 0x041541, b"\x03"),
        ],
    },
    "Always2DimensionDoorsPerDay": {
        True: [(EXE, 0x288360, b"\x61\x69\x64\x64")],
        False: [(EXE, 0x288360, b"\x61\x69\x74\x73")],
    },
    "RevertAdventureMapSpells": {
        True: [
            (EXE, 0x288360, b"\x74\x70\x64\x64"),
            (EXE, 0x01D51F, b"\x2c\x01"),
            (EXE, 0x01D534, b"\xc8\x00"),
            (EXE, 0x01D41F, b"\xc8\x00"),
        ],
        False: [
            (EXE, 0x288360, b"\x61\x69\x74\x73"),
            (EXE, 0x01D51F, b"\x90\x01"),
            (EXE, 0x01D534, b"\x2c\x01"),
            (EXE, 0x01D41F, b"\x2c\x01"),
        ],
    },
    "UnpredictableGenies": {
        True: [
            (EXE, 0x047BF1, b"\x31\xC9\x6A\x17\x5A\xE8\xC5\x4B\x0C\x00\x8A\x80\x1E\x7C\x44\x00\x8B\x55\x08\x8B\x0D\x20\x94\x69\x00\x6A\x06\x6A\x02\x6A\xFF\x6A\x01\x52\x50\xE8\x27\x85\x15\x00\xE9\xBF\x07\x00\x00\x1B\x1C\x1D\x1E\x1F\x20\x21\x24\x29\x2B\x2C\x2E\x30\x31\x33\x35\x37\x38\x3A\x25\x22\x41\x26\x12\x00"),
            (EXE, 0x048464, b"\xf1\x7b"),
        ],
        False: [
            (EXE, 0x047BF1, b"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x55\x8B\xEC\x51\x8B\x45\x08\x53\x56\x57\x85\xC0\x0F\x8C\xDD\x00\x00\x00\x3D\xBB\x00\x00\x00\x0F\x8D\xD2\x00\x00\x00\x8B\x15\x20\x94\x69\x00\x8D\x0C\xC5\x00\x00\x00\x00\x2B\xC8\xC1\xE1\x04\x8D\x8C\x11\xC4\x01\x00\x00\xE8"),
            (EXE, 0x048464, b"\x51\x83"),
        ],
    },
    "RevertOldHillFort": {
        True: [
            (EXE, 0x23EB50, b'\x00\x00\x80\x3E\x00\x00\x00\x3F\x00\x00\x40\x3F\x00\x00\x80\x3F\x00\x00\x80\x3F\x00\x00\x80\x3F'),
            (EXE, 0x26028A, b"\x6F"),
        ],
        False: [
            (EXE, 0x23EB50, b'\x00\x00\x80\x3F\x00\x00\x40\x3F\x00\x00\xA0\x3F\x00\x00\xC0\x3F\x00\x00\x00\x40\x00\x00\x40\x40'),
            (EXE, 0x26028A, b"\x66"),
        ],
    },
    "Level5Fangarm": {
        True: [(DAT, 0x1228, b"\x04")],
        False: [(DAT, 0x1228, b"\x05")],
    },
    "MonasteryRequiresBarracksAgain": {
        True: [(EXE, 0x23EDE8, b"\x21\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x29\x00\x00\x00\x22\x00\x00\x00\xFF\xFF\xFF\xFF\x24\x00\x00\x00\x22\x00\x00\x00")],
        False: [(EXE, 0x23EDE8, b"\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x29\x00\x00\x00\x22\x00\x00\x00\xFF\xFF\xFF\xFF\x24\x00\x00\x00\x22\x00\x00\x00\x21\x00\x00\x00")],
    },
    "RevertCloakOfTheUndeadKingChanges": {
        True: [
            (EXE, 0x0E3F33, b"\x3a"),
            (EXE, 0x0E3F2A, b"\x3c"),
            (EXE, 0x0E3F1F, b"\x40"),
            (DAT, 0x1AAE7, b"\x57\x61\x6C\x6B\x69\x6E\x67\x20\x44\x65\x61\x64\x0D\x0A\x41\x64\x76\x61\x6E\x63\x65\x64\x3A\x20\x57\x69\x67\x68\x74\x73\x0D\x0A\x45\x78\x70\x65\x72\x74\x3A\x20\x4C\x69\x63\x68\x65\x73\x20\x20\x20\x20\x20"),
            (EXE, 0x260B86, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x0E3F33, b"\x38"),
            (EXE, 0x0E3F2A, b"\x3a"),
            (EXE, 0x0E3F1F, b"\x3c"),
            (DAT, 0x1AAE7, b"\x53\x6B\x65\x6C\x65\x74\x6F\x6E\x73\x0D\x0A\x41\x64\x76\x61\x6E\x63\x65\x64\x3A\x20\x57\x61\x6C\x6B\x69\x6E\x67\x20\x44\x65\x61\x64\x0D\x0A\x45\x78\x70\x65\x72\x74\x3A\x20\x57\x69\x67\x68\x74\x73\x20\x20"),
            (EXE, 0x260B86, b"\x74\x73"),
        ],
    },
    "CatherineReplacesSorsha": {
        True: [
            (EXE, 0x27F09A, b"\x50\x50"),
            (EXE, 0x27F0AA, b"\x50\x50"),
            (EXE, 0x28873E, b"\x50\x50"),
            (EXE, 0x27F15A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27F09A, b"\x4B\x6E"),
            (EXE, 0x27F0AA, b"\x4B\x6E"),
            (EXE, 0x28873E, b"\x6F\x73"),
            (EXE, 0x27F15A, b"\x74\x73"),
        ],
    },
    "LegacySandro": {
        True: [
            (EXE, 0x27E80A, b"\x50\x50"),
            (EXE, 0x27E7FA, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E80A, b"\x4e\x63"),
            (EXE, 0x27E7FA, b"\x4e\x63"),
        ],
    },
    "LegacyCatherineReplacesSorsha": {
        True: [
            (EXE, 0x27F09A, b"\x50\x32"),
            (EXE, 0x27F0AA, b"\x50\x32"),
            (EXE, 0x28873E, b"\x50\x50"),
            (EXE, 0x27F15A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27F09A, b"\x4B\x6E"),
            (EXE, 0x27F0AA, b"\x4B\x6E"),
            (EXE, 0x28873E, b"\x6F\x73"),
            (EXE, 0x27F15A, b"\x74\x73"),
        ],
    },
    "LegacyLuna": {
        True: [
            (EXE, 0x27E03A, b"\x50\x50"),
            (EXE, 0x27E04A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E03A, b"\x65\x6c"),
            (EXE, 0x27E04A, b"\x65\x6c"),
        ],
    },
    "LegacyLordHaart": {
        True: [
            (EXE, 0x27F0BA, b"\x50\x50"),
            (EXE, 0x27F0CA, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27F0BA, b"\x4B\x6E"),
            (EXE, 0x27F0CA, b"\x4B\x6E"),
        ],
    },
    "LegacyRoland": {
        True: [
            (EXE, 0x27DE3A, b"\x50\x50"),
            (EXE, 0x27DE4A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27DE3A, b"\x53\x68"),
            (EXE, 0x27DE4A, b"\x53\x68"),
        ],
    },
    "LegacyGem": {
        True: [
            (EXE, 0x27EDDA, b"\x50\x50"),
            (EXE, 0x27EDEA, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27EDDA, b"\x44\x72"),
            (EXE, 0x27EDEA, b"\x44\x72"),
        ],
    },
    "LegacyHalon": {
        True: [
            (EXE, 0x27EC1A, b"\x50\x50"),
            (EXE, 0x27EC2A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27EC1A, b"\x57\x7a"),
            (EXE, 0x27EC2A, b"\x57\x7a"),
        ],
    },
    "LegacyAlamar": {
        True: [
            (EXE, 0x27E63A, b"\x50\x50"),
            (EXE, 0x27E64A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E63A, b"\x57\x6C"),
            (EXE, 0x27E64A, b"\x57\x6C"),
        ],
    },
    "LegacyYog": {
        True: [
            (EXE, 0x27E53A, b"\x50\x50"),
            (EXE, 0x27E54A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E53A, b"\x42\x72"),
            (EXE, 0x27E54A, b"\x42\x72"),
        ],
    },
    "LegacyCragHack": {
        True: [
            (EXE, 0x27E47A, b"\x50\x50"),
            (EXE, 0x27E48A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E47A, b"\x42\x72"),
            (EXE, 0x27E48A, b"\x42\x72"),
        ],
    },
    "StreamerRequest": {
        True: [
            (EXE, 0x27E51A, b"\x50\x50"),
            (EXE, 0x27E52A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E51A, b"\x42\x72"),
            (EXE, 0x27E52A, b"\x42\x72"),
        ],
    },
    "ConfluxRedesigned": {
        True: [
            (EXE, 0x28900A, b'\x50\x50'), 
            (EXE, 0x27551A, b'\x50'),
            (EXE, 0x23fb60, b'\x00'),
        ],
        False: [
            (EXE, 0x28900A, b'\x6e\x67'),
            (EXE, 0x27551A, b'\x74'),
            (EXE, 0x23fb60, b'\x26'),
        ],
    },
    "PrimaryStatsIncreaseIsConstant": {
        True: [
            (EXE, 0x18bb9a, b'\x50\x50')
        ],
        False: [
            (EXE, 0x18bb9a, b'\x74\x73')
        ],
    },
    "PitLordsCast3Times": {
        True: [
            (EXE, 0x27551B, b'\x50')
        ],
        False: [
            (EXE, 0x27551B, b'\x73')
        ],
    },
}

HEXPL = {
    "OdmówUmiejętności": {
        True: [(EXE, 0x0F9BA4, b"\xEB")],
        False: [(EXE, 0x0F9BA4, b"\x74")],
    },
    "RozproszenieTylkoNaPrzeciwnika": {
        True: [(EXE, 0x1A8477, b'\x8B\x55\x0C\x8B\x8F\xF4\x00\x00\x00\x39\xD1\x0F\x85\xB9\x00\x00\x00\xEB\x69')],
        False: [(EXE, 0x1A8477, b'\x8B\x8E\xC0\x53\x00\x00\x51\x8B\x4D\xFC\x6A\x23\xE8\x68\xCE\xF3\xFF\x83\xF8')],
    },
    "MaksymalneSzczęście4": {
        True: [
            (EXE, 0x03F658, b"\x04"),
            (EXE, 0x03F65F, b"\x04"),
            (EXE, 0x04153A, b"\x04"),
            (EXE, 0x041541, b"\x04"),
        ],
        False: [
            (EXE, 0x03F658, b"\x03"),
            (EXE, 0x03F65F, b"\x03"),
            (EXE, 0x04153A, b"\x03"),
            (EXE, 0x041541, b"\x03"),
        ],
    },
    "WrotaWymiarów2NaDzień": {
        True: [(EXE, 0x288362, b"\x64\x64")],
        False: [(EXE, 0x288362, b"\x74\x73")],
    },
    "PrzywrócCzaryMapyPrzygody": {
        True: [
            (EXE, 0x288360, b"\x74\x70\x64\x64"),
            (EXE, 0x01D51F, b"\x2c\x01"),
            (EXE, 0x01D534, b"\xc8\x00"),
            (EXE, 0x01D41F, b"\xc8\x00"),
        ],
        False: [
            (EXE, 0x288360, b"\x61\x69\x74\x73"),
            (EXE, 0x01D51F, b"\x90\x01"),
            (EXE, 0x01D534, b"\x2c\x01"),
            (EXE, 0x01D41F, b"\x2c\x01"),
        ],
    },
    "NieprzewidywalneDżiny": {
        True: [
            (EXE, 0x047BF1, b"\x31\xC9\x6A\x17\x5A\xE8\xC5\x4B\x0C\x00\x8A\x80\x1E\x7C\x44\x00\x8B\x55\x08\x8B\x0D\x20\x94\x69\x00\x6A\x06\x6A\x02\x6A\xFF\x6A\x01\x52\x50\xE8\x27\x85\x15\x00\xE9\xBF\x07\x00\x00\x1B\x1C\x1D\x1E\x1F\x20\x21\x24\x29\x2B\x2C\x2E\x30\x31\x33\x35\x37\x38\x3A\x25\x22\x41\x26\x12\x00"),
            (EXE, 0x048464, b"\xf1\x7b"),
        ],
        False: [
            (EXE, 0x047BF1, b"\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x55\x8B\xEC\x51\x8B\x45\x08\x53\x56\x57\x85\xC0\x0F\x8C\xDD\x00\x00\x00\x3D\xBB\x00\x00\x00\x0F\x8D\xD2\x00\x00\x00\x8B\x15\x20\x94\x69\x00\x8D\x0C\xC5\x00\x00\x00\x00\x2B\xC8\xC1\xE1\x04\x8D\x8C\x11\xC4\x01\x00\x00\xE8"),
            (EXE, 0x048464, b"\x51\x83"),
        ],
    },
    "PrzywrócStaryStaryFortNaWzgórzu": {
        True: [
            (EXE, 0x23EB50, b'\x00\x00\x80\x3E\x00\x00\x00\x3F\x00\x00\x40\x3F\x00\x00\x80\x3F\x00\x00\x80\x3F\x00\x00\x80\x3F'),
            (EXE, 0x26028A, b"\x6F"),
        ],
        False: [
            (EXE, 0x23EB50, b'\x00\x00\x80\x3F\x00\x00\x40\x3F\x00\x00\xA0\x3F\x00\x00\xC0\x3F\x00\x00\x00\x40\x00\x00\x40\x40'),
            (EXE, 0x26028A, b"\x66"),
        ],
    },
    "FangarmNa5Poziomie": {
        True: [(DAT, 0x1240, b"\x04")],
        False: [(DAT, 0x1240, b"\x05")],
    },
    "KlasztorBezKoszar": {
        True: [(EXE, 0x23EDE8, b"\x21\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x29\x00\x00\x00\x22\x00\x00\x00\xFF\xFF\xFF\xFF\x24\x00\x00\x00\x22\x00\x00\x00")],
        False: [(EXE, 0x23EDE8, b"\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x29\x00\x00\x00\x22\x00\x00\x00\xFF\xFF\xFF\xFF\x24\x00\x00\x00\x22\x00\x00\x00\x21\x00\x00\x00")],
    },
    "PrzywróćPłaszczNieumarłegoKróla": {
        True: [
            (EXE, 0x0E3F33, b"\x3a"),
            (EXE, 0x0E3F2A, b"\x3c"),
            (EXE, 0x0E3F1F, b"\x40"),
            (DAT, 0x1b601, b'\x6F\x64\x73\x74\x61\x77\x6F\x77\x79\x6D\x20\x77\x73\x6B\x72\x7A\x65\x73\x7A\x6F\x6E\x65\x20\x7A\x6F\x73\x74\x61\x6E\xB9\x20\x7A\x6F\x6D\x62\x69\x65\x2C\x20\x6E\x61\x20\x7A\x61\x61\x77\x61\x6E\x73\x6F\x77\x61\x6E\x79\x6D\x20\x75\x70\x69\x6F\x72\x79\x2C\x20\x61\x20\x6E\x61\x20\x6D\x69\x73\x74\x72\x7A\x6F\x77\x73\x6B\x69\x6D\x20\x6C\x69\x73\x7A\x65\x2E'),
            (EXE, 0x260B86, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x0E3F33, b"\x38"),
            (EXE, 0x0E3F2A, b"\x3a"),
            (EXE, 0x0E3F1F, b"\x3c"),
            (DAT, 0x1b601, b'\x7A\x61\x61\x77\x61\x6E\x73\x6F\x77\x6E\x79\x6D\x20\x77\x73\x6B\x72\x7A\x65\x73\x7A\x6F\x6E\x65\x20\x7A\x6F\x73\x74\x61\x6E\xB9\x20\x7A\x6F\x6D\x62\x69\x65\x2C\x20\x61\x20\x6E\x61\x20\x6D\x69\x73\x74\x72\x7A\x6F\x77\x73\x6B\x69\x6D\x20\x7A\x6A\x61\x77\x79\x2E\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20'),
            (EXE, 0x260B86, b"\x74\x73"),
        ],
    },
    "CatherineZastępujeSorshę": {
        True: [
            (EXE, 0x27F09A, b"\x50\x50"),
            (EXE, 0x27F0AA, b"\x50\x50"),
            (EXE, 0x28873E, b"\x50\x50"),
            (EXE, 0x27F15A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27F09A, b"\x4B\x6E"),
            (EXE, 0x27F0AA, b"\x4B\x6E"),
            (EXE, 0x28873E, b"\x6F\x73"),
            (EXE, 0x27F15A, b"\x74\x73"),
        ],
    },
    "Heroes2Sandro": {
        True: [
            (EXE, 0x27E80A, b"\x50\x50"),
            (EXE, 0x27E7FA, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E80A, b"\x4e\x63"),
            (EXE, 0x27E7FA, b"\x4e\x63"),
        ],
    },
    "CatherineZOdrodzeniaErathiiZastępujeSorshę": {
        True: [
            (EXE, 0x27F09A, b"\x50\x32"),
            (EXE, 0x27F0AA, b"\x50\x32"),
            (EXE, 0x28873E, b"\x50\x50"),
            (EXE, 0x27F15A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27F09A, b"\x4B\x6E"),
            (EXE, 0x27F0AA, b"\x4B\x6E"),
            (EXE, 0x28873E, b"\x6F\x73"),
            (EXE, 0x27F15A, b"\x74\x73"),
        ],
    },
    "Heroes2Luna": {
        True: [
            (EXE, 0x27E03A, b"\x50\x50"),
            (EXE, 0x27E04A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E03A, b"\x65\x6c"),
            (EXE, 0x27E04A, b"\x65\x6c"),
        ],
    },
    "Heroes2LordHaart": {
        True: [
            (EXE, 0x27F0BA, b"\x50\x50"),
            (EXE, 0x27F0CA, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27F0BA, b"\x4B\x6E"),
            (EXE, 0x27F0CA, b"\x4B\x6E"),
        ],
    },
    "Heroes2Roland": {
        True: [
            (EXE, 0x27DE3A, b"\x50\x50"),
            (EXE, 0x27DE4A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27DE3A, b"\x53\x68"),
            (EXE, 0x27DE4A, b"\x53\x68"),
        ],
    },
    "Heroes2Gem": {
        True: [
            (EXE, 0x27EDDA, b"\x50\x50"),
            (EXE, 0x27EDEA, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27EDDA, b"\x44\x72"),
            (EXE, 0x27EDEA, b"\x44\x72"),
        ],
    },
    "Heroes2Halon": {
        True: [
            (EXE, 0x27EC1A, b"\x50\x50"),
            (EXE, 0x27EC2A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27EC1A, b"\x57\x7a"),
            (EXE, 0x27EC2A, b"\x57\x7a"),
        ],
    },
    "Heroes2Alamar": {
        True: [
            (EXE, 0x27E63A, b"\x50\x50"),
            (EXE, 0x27E64A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E63A, b"\x57\x6C"),
            (EXE, 0x27E64A, b"\x57\x6C"),
        ],
    },
    "Heroes2Yog": {
        True: [
            (EXE, 0x27E53A, b"\x50\x50"),
            (EXE, 0x27E54A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E53A, b"\x42\x72"),
            (EXE, 0x27E54A, b"\x42\x72"),
        ],
    },
    "Heroes2CragHack": {
        True: [
            (EXE, 0x27E47A, b"\x50\x50"),
            (EXE, 0x27E48A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E47A, b"\x42\x72"),
            (EXE, 0x27E48A, b"\x42\x72"),
        ],
    },
    "StreamerRequest": {
        True: [
            (EXE, 0x27E51A, b"\x50\x50"),
            (EXE, 0x27E52A, b"\x50\x50"),
        ],
        False: [
            (EXE, 0x27E51A, b"\x42\x72"),
            (EXE, 0x27E52A, b"\x42\x72"),
        ],
    },
    "ZmianyWrótŻywiołów": {
        True: [
            (EXE, 0x28900A, b'\x50\x50'), 
            (EXE, 0x27551A, b'\x50'),
            (EXE, 0x23fb60, b'\x00'),
        ],
        False: [
            (EXE, 0x28900A, b'\x6e\x67'),
            (EXE, 0x27551A, b'\x74'),
            (EXE, 0x23fb60, b'\x26'),
        ],
    },
    "StałyWzrostUmiejętnościPodstawowych": {
        True: [
            (EXE, 0x18bb9a, b'\x50\x50')
        ],
        False: [
            (EXE, 0x18bb9a, b'\x74\x73')
        ],
    },
    "CzarciLordWskrzeszaTrzykrotnie": {
        True: [
            (EXE, 0x27551B, b'\x50')
        ],
        False: [
            (EXE, 0x27551B, b'\x73')
        ],
    },
}



# Read the INI file. 
script_dir = os.path.dirname(os.path.abspath(__file__))
ini_path = os.path.join(script_dir, 'PP.ini')
config = configparser.ConfigParser()
config.optionxform = str  # preserve original key casing
config.read(ini_path)
features = config['Optional features']
skins = config['Skins']
main = config['HexSwapper']
HEXES = {}
language = main.get('Language', fallback="en")
language_map = {
    "pl": HEXPL,
    "polish": HEXPL,
    "es": HEXES,
    "espanol": HEXES,
    "español": HEXES,
    "spanish": HEXES,
    "sp": HEXES,
}
#print("HEX keys available:", list(HEX.keys()))
#logging.info("Parsed INI keys: %s", list(features.items()))



#Core functionality - HexSwapping itself
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def swaphex(file, offset, bytes, description):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    if not os.path.isfile(path):
        logging.error("File not found: %s", path)
        raise FileNotFoundError(path)

    for _ in range(3):
        try:
            with open(path, "r+b") as f:
                f.seek(offset)
                f.write(bytes)
                f.flush()
                f.seek(offset)
                written = f.read(len(bytes))
                if written != bytes:
                    raise IOError("Verification failed")
            #logging.info("%s patched at 0x%X", description, offset) 
            return
        except PermissionError:
            time.sleep(0.5)
        except IOError as e:
            logging.error("IOError while verifying %s: %s", description, e)

    logging.error("Failed to patch %s at offset 0x%X", path, offset)
    logging.debug("Expected bytes: %s, got: %s", bytes, written)

def apply(name, state):
    patches = language_map.get(language.strip().lower(), HEX).get(name, {})
    if not patches:
        #logging.warning("Unknown key in INI: %s", name)
        return
    for target, offset, data in patches.get(state, []):
        swaphex(target, offset, data, name)


def convert_value(value):
    true_values = {'true', 'yes', 'on'}
    false_values = {'false', 'no', 'off'}

    lower_val = value.strip().lower()
    if lower_val in true_values:
        return True
    elif lower_val in false_values:
        return False
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value  # Return as string if no other conversion works


Always2DimensionDoorsPerDay = features.getboolean('Always2DimensionDoorsPerDay')
RevertAdventureMapSpells = features.getboolean('RevertAdventureMapSpells')
CatherineReplacesSorsha = features.getboolean('CatherineReplacesSorsha')
LegacyCatherineReplacesSorsha = features.getboolean('LegacyCatherineReplacesSorsha')


for section in config.sections():
    for key, value in config.items(section):
        state = convert_value(value)
        if key not in HEX:
            #logging.warning("Unknown key in INI: %s", key)
            continue
        apply(key, state)


if Always2DimensionDoorsPerDay and RevertAdventureMapSpells:
        logging.error("DD2perDay and RevertAdvMapSpells are incompatible")
        Always2DimensionDoorsPerDay = False
        apply("Always2DimensionDoorsPerDay", Always2DimensionDoorsPerDay)


if LegacyCatherineReplacesSorsha:
        CatherineReplacesSorsha = True
        apply("LegacyCatherineReplacesSorsha", LegacyCatherineReplacesSorsha)


#input("Press Enter to exit...")


