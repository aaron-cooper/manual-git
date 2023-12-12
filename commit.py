import os
from cryptography.hazmat.primitives import hashes
import binascii
import zlib
import stat
import time
import user
from config import ConfigError
import sys
import ignore


def init_if_necessary(root: str):
    init_dirs = [ # a new repo should have these directories
        r"/.git/",
        r"/.git/branches",
        r"/.git/hooks",
        r"/.git/objects",
        r"/.git/objects/pack",
        r"/.git/objects/info",
        r"/.git/info",
        r"/.git/refs",
        r"/.git/refs/tags",
        r"/.git/refs/heads",
    ]

    init_files = [ # a new repo should have these files (keys) containing this content (values)
        (r"/.git/HEAD", "ref: refs/heads/main\n"),
        (r"/.git/config", "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = true\n"),
        (r"/.git/description", ""),
        (r"/.git/info/exclude", "")
    ]

    if os.path.isdir(root + "/.git"): # if .git exists, assume it's a valid repo and return
        return

    for dir in init_dirs:
        os.mkdir(root + dir)

    for (file, content) in init_files:
        with open(root + file, "w") as f:
            f.write(content)

# Given a path, transform a file to a blob object. If the object isn't already
# stored in the repo, add it. Return the hash of the object as a string
def add_blob_object(path: str, options) -> bytes:
    with open(path, "rb") as f:
        file_content = f.read()
    obj_content = bytearray()
    obj_content += f"blob {len(file_content)}\0".encode()
    obj_content += file_content
    obj_content = bytes(obj_content)

    obj_hash = hash_array_of_bytes(obj_content)
    obj_hash_str = binascii.hexlify(obj_hash).decode()
    obj_content = zlib.compress(obj_content)

    obj_dir_path = options.root + "/.git/objects/" + obj_hash_str[0:2] + '/'
    obj_path = obj_dir_path + obj_hash_str[2:]

    if os.path.isfile(obj_path): #don't try to add the object again
        return obj_hash

    if not os.path.isdir(obj_dir_path):
        os.mkdir(obj_dir_path)

    with open(obj_dir_path + obj_hash_str[2:], "wb") as obj_file:
        obj_file.write(obj_content)

    return obj_hash

# Recursively traverses a directory creating blobs for any files found, and
# trees for any parents of the files. If the tree doesn't exist in the repo, add
# it. Return the hash of the tree. Skip the .git directory. This function
# assumes that the .git directory is a child of the working directory. If the
# path supplied points to a directory which doesn't have any files, and whose
# subdirectories don't contain any files, no tree object is created and None
# is returned
def add_tree_object(path: str, options) -> bytes | None:
    objects = []
    dir_content = os.listdir(path)
    dir_content.sort()
    for entry_name in filter(lambda x: x not in options.ignores, dir_content):
        p = path + '/' + entry_name
        if os.path.isdir(p):
            if tree := add_tree_object(p, options):
                objects.append((40000, entry_name, tree)) # 40000 = directory
        elif os.path.isfile(p):
            objects.append((get_file_type(p), entry_name, add_blob_object(p, options)))
    if len(objects) == 0:
        return None
    tree_content = bytearray()
    for (obj_type, obj_name, obj_hash) in objects:
        tree_content += f'{obj_type} {obj_name}\0'.encode()
        tree_content += obj_hash

    tree_content = bytes(f"tree {len(tree_content)}\0".encode() + tree_content)
    tree_hash = hash_array_of_bytes(tree_content)
    tree_hash_str = binascii.hexlify(tree_hash).decode()

    obj_dir_path = f"{options.root}/.git/objects/" + tree_hash_str[0:2]
    tree_obj_path = obj_dir_path + '/' + tree_hash_str[2:]

    if os.path.isfile(tree_obj_path):
        return tree_hash

    if not os.path.isdir(obj_dir_path):
        os.mkdir(obj_dir_path)

    with open(tree_obj_path, "wb") as f:
        f.write(zlib.compress(tree_content))

    return tree_hash

# Given a path to a file, return 100644, or 100755 if the file is executable,
# or 120000 if the file is a symlink
def get_file_type(path: str) -> int:
    file_stat = os.stat(path).st_mode
    if file_stat & stat.S_IXUSR != 0:
        return 100755
    elif file_stat & stat.S_ISLNK(file_stat) != 0:
        return 120000
    else:
        return 100644

def hash_array_of_bytes(message: bytes):
    sha1 = hashes.Hash(hashes.SHA1())
    sha1.update(message)
    return sha1.finalize()

# return (unix time, time zone)
def get_time_info() -> (int, int):
    if time.localtime().tm_isdst == 0:
        offset = time.timezone
    else:
        offset = time.altzone
    offset = int(-offset / (36))
    return (int(time.time()), offset)

# Add all of the objects in the cwd and create a commit object referencing them.
def add_commit_object(parent: bytes | None, options) -> bytes | None:
    user_name, user_email = user.get_user_info(f'{options.root}/.git/config')
    if not user_name or not user_email:
        raise ConfigError("Username and email missing, please set locally to allow creating commits.")

    root_tree = add_tree_object(options.root, options)
    if not root_tree:
        return None

    (curr_time, timezone) = get_time_info()

    commit_content = bytearray()
    commit_content += f"tree ".encode() + binascii.hexlify(root_tree) + b'\n'
    if parent:
        commit_content += f"parent ".encode() + binascii.hexlify(parent) + b'\n'
    commit_content += f"author {user_name} <{user_email}> {curr_time} {timezone:+05}\n".encode()
    commit_content += f"committer {user_name} <{user_email}> {curr_time} {timezone:+05}\n".encode()
    commit_content += f"\n\n{options.message}\n".encode()

    commit_content = bytes(f"commit {len(commit_content)}\0".encode() + commit_content)
    commit_hash = hash_array_of_bytes(commit_content)
    commit_hash_str = binascii.hexlify(commit_hash).decode()

    obj_dir_path = f"{options.root}/.git/objects/" + commit_hash_str[0:2]
    commit_path = obj_dir_path + '/' + commit_hash_str[2:]

    if os.path.isfile(commit_path):
        return commit_path

    if not os.path.isdir(obj_dir_path):
        os.mkdir(obj_dir_path)

    with open(commit_path, "wb") as f:
        f.write(zlib.compress(commit_content))

    return commit_hash

# return the commit hash of the commit pointed to by head, if it exists
# or None otherwise
def get_head(root: str) -> bytes | None:
    with open(f"{root}/.git/HEAD", "r") as f:
        head = f.read().strip()

    if head.startswith("ref: "):
        head = root + '/.git/' + head[5:]
        if not os.path.isfile(head):
            head = None
        else:
            with open(head, "r") as f:
                head = f.read().strip().encode()
    if head:
        head = binascii.a2b_hex(head)
    return head

def update_head(commit, root: str):
    commit = binascii.hexlify(commit).decode()
    with open(f"{root}/.git/HEAD", "r") as f:
        head = f.read().strip()

    if head.startswith("ref: "):
        path_to_update = root + '/.git/' + head[5:]
    else:
        path_to_update = root + '/.git/HEAD'

    with open(path_to_update, "w") as file_to_update:
        file_to_update.write(commit + '\n')


def commit(options):
    parent = get_head(options.root)
    new_commit = add_commit_object(parent, options)
    update_head(new_commit, options.root)



def main(ops):
    ops.ignores = ignore.get_ignore(ops.root)
    try:
        commit(ops)
    except ConfigError as e:
        print(e.args[0], file=sys.stderr)