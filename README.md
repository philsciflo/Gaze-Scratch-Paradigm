# Gaze-Scratch-Paradigm

***

Author(s): Florian Bednarski et al. (2023) <br>

***

## Description
In this repository you can find all materials required to replicate the gaze scratch paradigm. 

The gaze scratch paradigm is a gaze-contingent eye tracking paradigm. 
The design has been developed at the [Max Planck Institute for Human Cognitive and Brain Sciences](https://www.cbs.mpg.de/en) in Leipzig. 

The data shared via [OSF](https://osf.io/xrbzg/) is from a 
first sample of 45 infants (6-10 months-old). 
Parents were informed about the publication of the data and agreed by written consent to the anonymized 
publication.

**OSF project**: https://osf.io/xrbzg/

If you plan on working with the experimental code, analysis script or data please do not hesistate to get 
in touch. 
The purpose of this project always was to inspire furture research and motivate replication attempts!

## Contents
*In this repository you can find*

### Code 
#### Experimental code
`./Code/gaze_scratch_paradigm.py`

Experimental code to run the experiment in your labratory. 
In principle the code is ready to use with any Tobii eye tracker compatible with the Tobii SDK. 
Establishing compatibility with other eye tracking systems should be possible as long as those systems are compatible with python.

- pilot code to connect to eye tracker and retrieve gaze data
- script to run gaze scratch paradigm

#### Data processing script

`./Code/GSP_Data_Processing.py`

The analysis code was used to process the gaze data collected with the gaze scratch paradigm. 
This script should help you to process gaze points, filter fixations and manage data according to participants and trials.

OSF data can be downloaded with the following function: 
```python
download_study_data(stimuli_only=False, verbose=True)
``` 

Data processing can be done also via a shell/terminal:
```bash
python GSP_Data_Processing.py --id SUBJECT_ID --condition CONDITION
```
  
### Visual and auditory stimuli to be downloaded from OSF
`./Stimuli`

The visual and auditory stimuli were used in the gaze scratch paradigm. 
Those images, short videos and sound files are free to use, and we hope interested researchers find them useful.

- image stimuli
- video stimuli 
- attention getter videos
- audio files

### Data to be downloaded from OSF
`./Data`

The data was collected from 45 infants at the [Max Planck Institute for Human Cognitive and Brain Sciences](https://www.cbs.mpg.de/en) in Leipzig. 
This data is there for everyone to use. 
If you want to check our work or perform further analyses be our guest! 
We invite any one to advance this research and would be extremly greatful if you get in touch with any questions regarding this project.

- gaze data per infant and trial 
- screenshots from the final scratch result
 
## Main requiements to run this code are

- [tobii_research](https://developer.tobiipro.com/python/python-getting-started.html)
    
**Notice**: `tobii SDK` is onyl compatible with `Python 3.6` (or `2.7`)
      
- [tkinter](https://docs.python.org/3/library/tk.html)

Some of this work is based on other pyhton and eye tracking projects. Two important sources of information and code are:

- https://github.com/titoghose/PyTrack
    
    Ghose, U., Srinivasan, A. A., Boyce, W. P., Xu, H., & Chng, E. S. (2020). PyTrack: An end-to-end analysis toolkit for eye tracking. Behavior research methods, 52, 2588-2603.
___
- https://github.com/esdalmaijer/PyGaze

    Dalmaijer, E.S., Mathôt, S., & Van der Stigchel, S. (2013). PyGaze: an open-source, cross-platform toolbox for minimal-effort programming of eye                  tracking experiments. Behaviour Research Methods. doi:10.3758/s13428-013-0422-2
___   
      
## Disclaimer
This is my very first python and developmental psychology project. 
The code might not be up to professional standards and the organisation and commenting will most likely confuse more experienced users. 
Please be patient I will try to improve things along the way and am always happy to help out with troubleshooting and questions.

## Citation 
In case you use this code or data please cite the following paper:

Bednarski, F. M., Rothmaler, K., Hofmann, S. M., & Grosse Wiesmann, C. (2025). Infants in Control—Evidence for Agency in 6‐to 10‐Months‐Old Infants in a Gaze‐Contingent Eye Tracking Paradigm. Child Development.
