#include "PrettyProgressIcon.hpp"


PrettyProgressIcon::PrettyProgressIcon(int stepChange)
{
    stepChange = stepChange;
    updateStep = stepChange;
    iconStep = 0;
}

char PrettyProgressIcon::get(){
    return icons[iconStep];
}

void PrettyProgressIcon::next(){
    updateStep++;
    if(updateStep < stepChange){
        return;
    }

    iconStep++;
    if(iconStep == sizeof(icons)){
        iconStep = 0;
    }
}

PrettyProgressIcon::~PrettyProgressIcon()
{
}
