# Gaze-Scratch-Paradigm
Repository for all materials required to replicate the gaze scratch paradigm.

DISCLAIMER
This is my very first python and developmental psychology project. The code might not be up to professional standards and the organisation and commenting will most likely confuse more experienced users. Please be patient I will try to improve things along the way and am always happy to help out with trouble shooting and questions.

DESCRIPTION
Here in this place you can find all materials required to replicate the gaze scratch paradigm. The gaze scratch paradigm is a gaze-contingent eye tracking paradigm. The design has been developed at the Max Planck Institute for Human Cognitive and Brain Sciences in Leipzig. The data uploaded here is from a first sample of 45 six to ten months-old infants. Parents were informed about the publication of the data and agreed by written consent to the anonymized publication. If you plan on working with the experimental code, analysis script or data please do not hesistate to get in touch. The purpose of this project always was to inspire furture research and motivate replication attempts!

    In this repository you can find the experimental code to run the experiment in your labratory. In principle the code is ready to use with any Tobii eye tracker compatible with the Tobii SDK. Establishing compatibility with other eye tracking systems should be possible as long as those systems are compatible with python. 

    In this repository you can find the visual and auditory stimuli used in the gaze scratch paradigm. Those images, short videos and sound files are free to use and we hope interested researchers find them usefull.

    In this repository you can find the analysis script used to process the gaze data collected with the gaze scratch paradigm. This script should help you to process gaze points, filter fixations and manage data according to participants and trials. 

    In this repository you can find the data collected from 45 infants at the Max Planck Institute for Human Cognitive and Brain Sciences in Leipzig. This data is there for everyone to use. If you want to check our work or perform further analyses be our guest! We invite any one to advance this research and would be extremly greatful if you get in touch with any questions regarding this project. 

CONTENTS

A. experimental code

    - pilot code to connect to eye tracker and retrieve gaze data
    
    - script to run gaze scratch paradigm
  
B. visual and auditory stimuli

    - image stimuli
    
    - video stimuli
    
    - attention getter videos
    
    - audio files

C. analysis script

    - data processing script 

D. data 

    - gaze data per infant and trial
    
    - screen shots from the final scratch result
 
Main requiements to run this code are:

    - tobii_research  (https://developer.tobiipro.com/python/python-getting-started.html)
    
      NOTICE: tobii SDK is onyl compatible with Python 3.6 or 2.7
      
    - tkinter         (https://docs.python.org/3/library/tk.html)

Some of this work is based on other pyhton and eye tracking projects. Two important sources of information and code are:

    - https://github.com/titoghose/PyTrack
    
    Ghose, U., Srinivasan, A. A., Boyce, W. P., Xu, H., & Chng, E. S. (2020). PyTrack: An end-to-end analysis toolkit for eye tracking. Behavior research methods, 52, 2588-2603.
    
    - https://github.com/esdalmaijer/PyGaze
    
    Dalmaijer, E.S., Mathôt, S., & Van der Stigchel, S. (2013). PyGaze: an open-source, cross-platform toolbox for minimal-effort programming of eye                  tracking experiments. Behaviour Research Methods. doi:10.3758/s13428-013-0422-2
      
      
