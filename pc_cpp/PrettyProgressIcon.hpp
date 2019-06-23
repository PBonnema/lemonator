#pragma once

class PrettyProgressIcon
{
private:
    char* icons = "\\|/-";
    int iconStep;
    int updateStep;
    int stepChange;
public:
    PrettyProgressIcon(int stepChange = 2);
    ~PrettyProgressIcon();
    void next();
    char get();
};