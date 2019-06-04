[![Coverage Status](https://coveralls.io/repos/github/PBonnema/lemonator/badge.svg)](https://coveralls.io/github/PBonnema/lemonator)
## The Lemonator

Team members:
- Peter Bonnema
- Mike Hilhorst
- Wiebe van Breukelen

## Installation
To pull all the required dependencies, please run the following commands within the shell:"

```bash

git submodule init
git submodule update

```

### Branches
- The code within the **master** branch is considered final. This means that it is well tested and reviewed by all the teammembers.
- The **development** branch will contain code that is considered as work in progress.
- The branches with the prefix **feature-** are used to develop new features. Eventually, they will be merged to development using pull requests. These pull requests should always be reviewed by a team member who is not assigned onto this specific feature.

### Testing procedure
Tests are formulated within the /tests folder. During the development process, testing are performed locally and remotely using Travis.CI
All test should pass before merging to development and master can be performed. 

## IDE
We're using Visual Studio Code as our IDE. Please install the following plugins to setup your work environment:
- autoDocstring; generating python docstrings.
- C/C++; C++ plugin for VS code.
- Catch2 and Google Test Explorer; Testing integration within VS code.
- Clang-format; For automatic formatting.
- Doxygen Documetation Generator
- Python
