import os
import options
import commit


def init_if_necessary():
    init_dirs = [ # a new repo should have these directories
        r"./.git/",
        r"./.git/branches",
        r"./.git/hooks",
        r"./.git/objects",
        r"./.git/objects/pack",
        r"./.git/objects/info",
        r"./.git/info",
        r"./.git/refs",
        r"./.git/refs/tags",
        r"./.git/refs/heads",
    ]

    init_files = [ # a new repo should have these files (keys) containing this content (values)
        (r"./.git/HEAD", "ref: refs/heads/main\n"),
        (r"./.git/config", "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = true\n"),
        (r"./.git/description", ""),
        (r"./.git/info/exclude", "")
    ]

    if os.path.isdir("./.git"): # if .git exists, assume it's a valid repo and return
        return

    for dir in init_dirs:
        os.mkdir(dir)

    for (file, content) in init_files:
        with open(file, "w") as f:
            f.write(content)

def main():
    ops = options.from_argv()
    init_if_necessary()
    match ops.command:
        case "commit":
            commit.main(ops)

if __name__ == "__main__":
    main()