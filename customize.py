#!/usr/bin/env python3

import sys
import os
import shutil
from subprocess import *

ROOTFS = "rootfs"
SKELETON = "skeleton"
BUILD = "build"

BASE_URL = "https://bitbucket.org/bhteam/bhware-drunkstar/downloads/"
PACKAGES = [
    "drunkstar_core.tar.bz2",
    "drunkstar_python-2.7.6_mercurial-2.9.2.tar.bz2",
    "drunkstar_python-3.4.2_pyserial-2.7.tar.bz2",
    "drunkstar_opencv-2.4.8.tar.bz2",
    "drunkstar_nginx-1.7.9.tar.bz2",
    "drunkstar_rsync-3.1.1.tar.bz2",
    "drunkstar_openssh-6.8p1.tar.bz2",
]

WIFI_SSID = ""
WIFI_PASSWORD = ""


def get_wifi_settings():
    global WIFI_SSID
    global WIFI_PASSWORD
    print("Enter the Wifi SSID:")
    WIFI_SSID = sys.stdin.readline().strip()
    print("Enter the Wifi password:")
    WIFI_PASSWORD = sys.stdin.readline().strip()


def download():
    if not os.path.exists(BUILD):
        os.mkdir(BUILD)
    if not os.path.exists("dl"):
        os.mkdir("dl")
    for package in PACKAGES:
        local = "dl/" + package
        if not os.path.exists(local):
            call(["wget", "-O", local, BASE_URL + package])
    if not os.path.exists("dl/dotvim"):
        print("Download VIM customization")
        call(["git", "clone", "https://github.com/alberthier/dotvim.git", "dotvim"], cwd = "dl")
        call(["git", "submodule", "init"], cwd = "dl/dotvim")
        call(["git", "submodule", "update"], cwd = "dl/dotvim")
        shutil.rmtree("dl/dotvim/.git")
        os.remove("dl/dotvim/.gitignore")
        os.remove("dl/dotvim/.gitmodules")


def cleanup():
    if os.path.exists(ROOTFS):
        print("Removing previous rootfs...")
        shutil.rmtree(ROOTFS)


def install_core():
    os.mkdir(ROOTFS)
    print("Extracting Drunkstar Core...")
    for archive in PACKAGES:
        call(["tar", "xjf", "dl/" + archive, "-C", ROOTFS])
    # remove VIM documentation
    shutil.rmtree(ROOTFS + "/usr/share/vim/vim73/doc")


def install_skeleton():
    print("Installing customized skeleton...")
    for f in os.listdir(SKELETON):
        call(["cp", "-rf", os.path.join(SKELETON, f), ROOTFS])

    print("VIM customization")
    call(["cp", "-rf", "dl/dotvim", ROOTFS + "/root/.vim"])
    call(["ln", "-s", ".vim/vimrc", ".vimrc"], cwd = ROOTFS + "/root")

    print("Wifi customization")
    for conf_file in ["/etc/hostapd.conf", "/etc/wpa_supplicant/wpa_supplicant.conf"]:
        f = open(ROOTFS + conf_file)
        conf = f.read()
        f.close()
        conf = conf.replace("@@__BH_WIFI_SSID__@@", WIFI_SSID)
        conf = conf.replace("@@__BH_WIFI_PASSWORD__@@", WIFI_PASSWORD)
        f = open(ROOTFS + conf_file, "w")
        f.write(conf)
        f.close()


def make_ubi_image():
    print("Create UBI image")
    drunkstar_cfg = BUILD + "/drunkstar.cfg"
    drunkstar_ubifs = BUILD + "/drunkstar.ubifs"
    drunkstar_ubi =  ROOTFS + "/root/install/drunkstar.ubi"

    f = open(drunkstar_cfg, "w")
    f.write("[ubifs]\n")
    f.write("image=" + drunkstar_ubifs + "\n")
    f.write("mode=ubi\n")
    f.write("vol_id=0\n")
    f.write("vol_type=dynamic\n")
    f.write("vol_name=rootfs\n")
    f.write("vol_alignment=1\n")
    f.write("vol_flags=autoresize\n")
    f.close()

    call(["mkfs.ubifs", "--leb-size=0x1f800", "--min-io-size=0x800", "--max-leb-cnt=2048", "--compr=lzo", "--root=rootfs", drunkstar_ubifs])
    call(["ubinize", "--peb-size=0x20000", "--sub-page-size=512", "--min-io-size=0x800", "-o", drunkstar_ubi, drunkstar_cfg])

    os.remove(drunkstar_cfg)
    os.remove(drunkstar_ubifs)


def make_archive():
    print("Create USB key archive")
    content = os.listdir(ROOTFS)
    call(["tar", "cjf", "../" + BUILD + "/drunkstar.tar.bz2", "."], cwd = ROOTFS)


if __name__ == "__main__":
    # cd to the script directory
    if os.getuid() != 0:
        print("You must run this program as root")
    else:
        os.chdir(os.path.dirname(__file__))
        get_wifi_settings()
        download()
        cleanup()
        install_core()
        install_skeleton()
        make_ubi_image()
        make_archive()
