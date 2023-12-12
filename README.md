# Manual Git
### I made this repository without using Git!
Or more specifically, my local copy of this repository, which was later pushed to GitHub, was created without using Git.

## What exactly do you mean by that?
This repository was created using only the code committed to this repository. The code doesn't use any Git library, nor does it call Git commands. Instead I recreated a small subset of Git's functionality, just the stuff needed to commit this code to a repository that Git would recognize as valid.

The only times I used Git during the development process was to ensure that the repository I was creating was valid in Git's eyes (for that I used `git log` and `git show`), as well as pushing this repository to GitHub, since reimplementing the Git Push command was a whole can of worms I didn't want to open.

## Why?
I think Git's pretty cool, and I wanted to get a deeper understanding of how it works behind the scenes so that I could become a more powerful Git user. I'm a learn-by-doing kind of person, so I decided that this would be a fun and effective way to accomplish that goal.

The code in this repo is not complete or robust, it is very breakable and you should not use it (and you may not use it).

## What functionality have you implemented?
My code can:
- Initialize a Git repository (happens automatically when any of this code is run)
- Add files to that repository as blob objects
- Create and add tree objects, reflecting the working directory
- Create and add commit objects
- Update HEAD when a commit is made, including updating whatever branch HEAD references
- Allow the user to add basic configs to the repository (the user must set their name and email to create commits)
- Allow the user to add a remote
- Ignore things in the .mgitignore file (does not work the same or as well as a .gitignore)

Note: even though this repository is flat, my code can handle committing tree directory structures just fine.

## What resources did you refer to?
[Chapter 10 of "Pro Git"](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) for an overview of Git's internals, and [Git's documentation](https://git-scm.com/docs) more in-depth descriptions of file formats and things. I also created some dummy repos that I could reverse engineer.