# Music-Models
[Merrick Ohata](https://www.merrickohata.xyz), Prajakta Bedekar, Dan Q Naiman
2022-2023

## Introduction

Program to statistically analyze melodies in [abc notation](https://abcnotation.com/) format and extract the time-dependent Markov transition matrix. Each transition probability takes the form of a Beta distribution. 

This code and its results were used in [Music as Math: A Time-Dependent Markov Model for Irish Folktune Melodies]() by applying it to the [abc version of the Nottingham Music Database](https://abc.sourceforge.net/NMD/). The data used is included here to easily reproduce any results. This program may also be used on any collection of music in the abc format.

### Table of Contents
1. [Introduction](#Introduction)
2. [Starting Functions](#Starting-Functions)
3. [note](#note)
4. [key_length](#key_length)



## Starting Functions
* **[sjkabcfunc](sjkabcfunc.py)** contains a number of existing functions from the [sjkabc library](https://github.com/sjktje/sjkabc/blob/develop/docs/index.rst) to aid in data processing. These include functions such as to get information from header fields, expand repeat signs, and remove information such as chords, articulations, or expression markers.

## [note](note.py)
defines note objects
### class: note
* **input: pitch |** int: pitch class notation for the pitch
* **input: duration |** frac: duration of the note
---
#### properties
* **pitch |** int: the pitch
* **duration |** frac: the duration
* **note |** tuple: (pitch, duration)

## [key_length](key_length.py) 
* defines keys and keycenters for determining how to normalize/transpose melodies into a keycenter of C.

### class: song_div
an object to define the time signature of a song
* **input: leninfo |** the top number in a time signature
* **input: timeinfo |** the bottom number in a time signature
---
#### properties
* **default_length |** the default length for a note in the abc notation for the song. This is essentially 1/timeinfo

### class: song_key
the key of a song
* **input: keyinfo |** the raw information of the key
---
#### properties
* **key_raw |** str: the raw key_info
* **pkeymode |** str: the mode of the key
  * ex. dorian, mixolydian, etc
* **keycenter |** str: the key center of the key 
  * ex. the key center of G major is G
* **relative_major |** str: the relative major of the key 
  * ex. the relative major of A# minor is C#
* **keymap |** dict: dictionary of flat/sharp modifiers for the key
  * ex the keymap for Bb major is `{'A': 'A', 'B': '_B', 'C': 'C', 'D': 'D', 'E': '_E', 'F': 'F', 'G': 'G', ' ': ' ', 'Z': 'Z'}`

## [song_processer](song_processer.py)
* combines functions from [sjkabcfunc](sjkabcfunc.py) and [key_length](key_length.py) to process abc notation songs. 
* processes abc notation songs into post_song objects, which contain representations of melodies in (pitch, duration) pairs. objects also contain mappings with (pitch, duration) pairs normalized such that keycenter of the melody is 0. 

### function: expand_music
Strips chords, expands repeats, and strips extra characters from an abc notation file
* **input: music |** string: abc notation song
* **output: music |** string: expanded abc notation, all in uppercase

### function: pitch_class_representation
converts notes in abc notation into pitch class notation (an integer in base 12)
* **input: notes |** string: a string of notes given in abc notation as (^_=)(ABCDEFG) sequence
* **output: pcr |** list of integers: pitch class representation of note(s) - integers in base 12

### function: key_signature_mapping
adds accidentals; maps a melody to its keymap 
* **input: music |** str: stripped and expanded music; output from expand_music
* **input: keymap |** dict: a key_length.song_key.keymap
* **output: converted |** str: music with accidentals to match the keymap

### class: pre_song
essentially a tune object from ajkabc. Called pre-song as it is a pre-processing song before we use it. Has properties as defined by the header lines in abc content and song content that has not been modified.

### class: post_song
processed song with the information that we want
* **input: pre_song |** a pre_song object 
---
#### properties
* **pre |** pre_song: the pre_song version of the post_song
* **music |** str: the expanded and stripped abc version of the pre_song
* **given_key |** key_length.song_key: of the song
* **key_center |** int: the pitch class representation of the key of the given_key
* **default_keymap |** dict: the keymap of the given_key
* **pitches |** list: all pitches in order of the song
* **durations |** list: all durations in order of the song
* **notelist |** list(note.notes): list of note objects
* **transposed_pitches |** list(int): self.pitches transposed to be centered around pitch class 0
* **total_duration |** frac: the sum of all durations in self.durations
---
#### methods
* **do_mapping |** returns string of self.music with added accidentals from the keymap
* **extract_notes |** sets attributes of pitches, durations, and notelist 

* 

