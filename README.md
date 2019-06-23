## The Lemonator

Team members:
- Peter Bonnema
- Mike Hilhorst
- Wiebe van Breukelen

## CI

master: [![Build Status](https://travis-ci.com/PBonnema/lemonator.svg?branch=dev)](https://travis-ci.com/PBonnema/lemonator)[![Coverage Status](https://coveralls.io/repos/github/PBonnema/lemonator/badge.svg)](https://coveralls.io/github/PBonnema/lemonator)

dev: [![Build Status](https://travis-ci.com/PBonnema/lemonator.svg?branch=dev)](https://travis-ci.com/PBonnema/lemonator)[![Coverage Status](https://coveralls.io/repos/github/PBonnema/lemonator/badge.svg?branch=dev)](https://coveralls.io/github/PBonnema/lemonator?branch=dev)

## Installation
Make sure you are running Python 3.7.* 32-bits. The 64-bits edition is known to have issues with pybind and the TDM-GCC-64 compiler.

To pull all the required dependencies, please run the following commands within a shell:"

```bash

git submodule init
git submodule update

```

Then, you will need to install the required compilers:
  - [TDM-GCC-32](http://tdm-gcc.tdragon.net/download), download version 5.1.0-3 32-bits edition.
  - [arm-none-eabi toolchain](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads), download latest version.
  
You will have to setup [bmptk](http://github.com/wovo/bmptk) and [hwlib](http://github.com/wovo/hwlib)(with pybind support) aswell.

### Branches
- The code within the **master** branch is considered final. This means that it is well tested and reviewed by all the teammembers.
- The **development** branch will contain code that is considered as work in progress.
- The branches with the prefix **feature-** are used to develop new features. Eventually, they will be merged to development using pull requests. These pull requests should always be reviewed by a team member who is not assigned onto this specific feature.

### Testing procedure
Tests are located within the ./tests folder. During the development process, tests are performed locally and remotely using Travis-CI.
All test should pass before merging to development and master. 

You may run the following command to test locally:
```bash
/somewhere/on/your/disk/lemonator (dev)
$ python -m unittest -v
```

Or: 
```bash
/somewhere/on/your/disk/lemonator (dev)
$ coverage run --branch --source ./simulator --omit=./simulator/*.pyc,./simulator/Interface.py,./simulator/main.py -m unittest -v
```

To also generate a coverage report. You can also use any Python test explorer in any IDE.

## IDE
We're using Visual Studio Code as our IDE. Please install the following plugins to setup your work environment:
- autoDocstring; generating python docstrings.
- C/C++; C++ plugin for VS code.
- Catch2 and Google Test Explorer; Testing integration within VS code.
- Python 3
