#!/bin/bash

# amixer cset name='Headphone Playback Volume' 63

export LD_LIBRARY_PATH=`pwd`/../sw-trigger-cpp/build:/home/use/projets/2022-02_Orgue_Electronique/work/sw-trigger-cpp/build/src/synth/fluidsynth/src/:/home/use/projets/2022-02_Orgue_Electronique/work/sw-trigger-cpp/build/src/synth/libsynthlib.so

../lv_micropython/ports/unix/micropython -X heapsize=10M player.py


