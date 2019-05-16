## Building Guide

1. Install the latest 64 bits TDM-GCC compiler: http://tdm-gcc.tdragon.net/download (Accept the default path within the installer)
2. Install the ARM-none-eabi toolchain: 
[https://developer.arm.com/-/media/Files/downloads/gnu-rm/8-2018q4/gcc-arm-none-eabi-8-2018-q4-major-win32-sha2.exe?revision=169eed21-7cbc-48c6-a289-f39d95bd634c?product=GNU%20Arm%20Embedded%20Toolchain,32-bit,,Windows,8-2018-q4-major](Download) 
(Accept the default path within the installer)
3. Create the folder C:\ti-software Then proceed to step 4 and clone all repos within these folders.
4. Clone [bmptk](https://github.com/wovo/bmptk) into this folder.
5. Clone [hwlib](https://github.com/wovo/hwlib) with the following commands:
```bash
git clone -n [REPO]
git checkout 4d9eac3
```
Newer versions cause problems.
6. Clone [pybind11](https://github.com/pybind/pybind11)
7. Compile pybind11 (see the installation instructions: https://pybind11.readthedocs.io/en/master/basics.html#compiling-the-test-cases)
8. Ask Wiebe to apply patches.














































^G Get Help      ^O Write Out     ^W Where Is      ^K Cut Text      ^J Justify       ^C Cur Pos       M-U Undo         M-A Mark Text    M-] To Bracket   M-▲ Previous     ^B Back          ^◀ Prev Word
^X Exit          ^R Read File     ^\ Replace       ^U Uncut Text    ^T To Spell      ^_ Go To Line    M-E Redo         M-6 Copy Text    M-W WhereIs Next M-▼ Next         ^F Forward       ^▶ Next Word
)

