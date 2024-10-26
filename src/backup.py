import os
from typing import List, Tuple
import py7zr
import hashlib
import logging

_log = logging.getLogger("Backup")
_log.addHandler(logging.StreamHandler())
_log.setLevel(logging.INFO)
_log.info("Initializing backup logic")

source_location = "B:\\documents"
final_location = "B:\\Local Google Drive\\documents"

CHECKSUM_FILE_NAME = "checksum.txt"


def hash_unchanged(folder: str, files: List[str]):
    digest = None
    checksum_file = os.path.join(folder, CHECKSUM_FILE_NAME)
    if len(files) == 0:
        return True, "None", checksum_file
    for file in files:
        if file == CHECKSUM_FILE_NAME:
            continue
        filepath = os.path.join(folder, file)
        with open(filepath, "rb") as f:
            if digest is None:
                digest = hashlib.file_digest(f, hashlib.sha3_256)
            else:
                digest.update(hashlib.file_digest(f, hashlib.sha3_256).hexdigest().encode())
                pass
    if not digest:
        return True, "None", checksum_file
    digest = digest.hexdigest()
    _log.debug("Computed digest for %s is %s", folder, digest)

    if os.path.exists(checksum_file):
        with open(checksum_file, "r") as c:
            old_digest = c.readline()
            if old_digest == digest:
                return True, digest, checksum_file
    return False, digest, checksum_file


def get_filters(path: str):
    if "Bilder" in path:
        compression = 0
    else:
        compression = 7
    return [{'id': py7zr.FILTER_X86}, {'id': py7zr.FILTER_LZMA2, 'preset': compression}, {'id': py7zr.FILTER_CRYPTO_AES256_SHA256}]


HashOk = bool
FileHash = str
ChecksumPath = str

def bundle_files(
    password: str, folder: str, files: List[str], archive_destination: str
) -> Tuple[HashOk, FileHash, ChecksumPath]:
    # direct folder content will be moved into an archive with the folder's name, into a folder of the same name
    if not os.path.exists(archive_destination):
        os.mkdir(archive_destination)

    hash_ok, current_hash, checksum_file = hash_unchanged(folder, files)
    if hash_ok:
        _log.debug("Hash is unchanged for %s's files", folder)
        return True

    archive_destination = os.path.join(archive_destination, os.path.basename(archive_destination)) + ".7z"

    with py7zr.SevenZipFile(
        archive_destination, "w", password=password, filters=get_filters(folder), mp=True
    ) as archive:
        _log.debug("Hash changed for %s. Updating.", folder)
        for file in files:
            filepath = os.path.join(folder, file)
            archive.write(filepath, file)
        # write checksum only after archive has been created at least once.
        with open(checksum_file, "w") as c:
            c.write(current_hash)
        archive.write(checksum_file, os.path.basename(checksum_file))


def hash_subdirs(folder: str):
    digest = hashlib.sha3_256()
    for subfolder, _, files in os.walk(folder):
        for file in files:
            if file == CHECKSUM_FILE_NAME:
                continue
            filepath = os.path.join(subfolder, file)
            with open(filepath, "rb") as f:
                digest.update(hashlib.file_digest(f, hashlib.sha3_256).hexdigest().encode())
    return digest


def read_hash(checksum_path: str):
    if os.path.exists(checksum_path):
        with open(checksum_path, "r") as f:
            return f.read()
    else:
        return None


def update_subdir_hash(checksum_path: str, digest: str):
    with open(checksum_path, "w") as f:
        f.write(digest)


def has_subdir_changed(folder: str):
    digest = hash_subdirs(folder).hexdigest()
    checksum_path = os.path.join(folder, CHECKSUM_FILE_NAME)
    old_hash = read_hash(checksum_path)
    if digest != old_hash:
        update_subdir_hash(checksum_path, digest)
        return True
    return False


def _encrypt(password: str, folder: str, files: List[str], max_depth=0, base_depth=0):
    depth = len(folder.split(os.path.sep)) - base_depth
    archive_destination = folder.replace(source_location, final_location)
    if max_depth < depth:
        _log.info("Skipping folder %s as it's already part of a subdir archive of ancestor", folder)
    elif max_depth > depth:
        if files:
            _log.info("Bundling files of %s and drilling deeper next", folder)
            bundle_files(password, folder, files, archive_destination)
        else:
            _log.info("Empty folder %s. No files to bundle", folder)
    else:
        if has_subdir_changed(folder):
            _log.info("Creating subdirectory archive for %s", folder)
            destination_parent = os.path.dirname(archive_destination)
            if not os.path.exists(destination_parent):
                os.makedirs(destination_parent)
            with py7zr.SevenZipFile(
                archive_destination + ".7z", "w", password=password, filters=get_filters(folder), mp=True
            ) as archive:
                archive.writeall(folder, os.path.basename(folder))
        else:
            _log.info("Subdirectory %s is unchanged", folder)


def encrypt(source_path, archive_depth=0, password=None):
    if not password:
        password = input("Please enter the archive password:\n")
    else:
        password = "test"
    for folder, _, files in os.walk(source_location):
        _encrypt(password, folder, files, archive_depth, len(source_path.split(os.path.sep)))


encrypt(source_location, archive_depth=2)
