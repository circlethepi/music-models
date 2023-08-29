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
4. [key_length](#keylength)
5. [song_processor](#songprocessor)
6. [dataset_creator](#datasetcreator)
7. [data_analyzer](#dataanalyzer)



## Starting Functions
* **[sjkabcfunc](sjkabcfunc.py)** contains a number of existing functions from the [sjkabc library](https://github.com/sjktje/sjkabc/blob/develop/docs/index.rst) to aid in data processing. These include functions such as to get information from header fields, expand repeat signs, and remove information such as chords, articulations, or expression markers.

## [note](note.py)
defines `note` objects
### class: note
* **input: pitch |** `int`: pitch class notation for the pitch
* **input: duration |** `frac`: duration of the note
---
#### properties
* **pitch |** `int`: the pitch
* **duration |** `frac`: the duration
* **note |** `tuple`: (pitch, duration)

## [key_length](key_length.py) 
* defines keys and keycenters for determining how to normalize/transpose melodies into a keycenter of C.

### class: song_div
an object to define the time signature of a song
* **input: leninfo |** `int`: the top number in a time signature
* **input: timeinfo |** `int`: the bottom number in a time signature
---
#### properties
* **default_length |** `frac`: the default length for a note in the abc notation for the song. This is essentially 1/timeinfo

### class: song_key
the key of a song
* **input: keyinfo |** `str`: the raw information of the key
---
#### properties
* **key_raw |** `str`: the raw keyinfo (input)
* **keymode |** `str`: the mode of the key
  * ex. dorian, mixolydian, etc
* **keycenter |** `str`: the key center of the key 
  * ex. the key center of G major is G
* **relative_major |** `str`: the relative major of the key 
  * ex. the relative major of A# minor is C#
* **keymap |** `dict`: dictionary of flat/sharp modifiers for the key in abc convention
  * ex the keymap for Bb major is `{'A': 'A', 'B': '_B', 'C': 'C', 'D': 'D', 'E': '_E', 'F': 'F', 'G': 'G', ' ': ' ', 'Z': 'Z'}`

## [song_processor](song_processor.py)
* combines functions from [sjkabcfunc](sjkabcfunc.py) and [key_length](key_length.py) to process abc notation songs. 
* processes abc notation songs into post_song objects, which contain representations of melodies in (pitch, duration) pairs. objects also contain mappings with (pitch, duration) pairs normalized such that keycenter of the melody is 0. 

### function: expand_music
Strips chords, expands repeats, and strips extra characters from an abc notation file
* **input: music |** `str`: abc notation song
* **output: music |** `str`: expanded abc notation, all in uppercase

### function: pitch_class_representation
converts notes in abc notation into pitch class notation (an integer in base 12)
* **input: notes |** `str`: a string of notes given in abc notation as (^_=)(ABCDEFG) sequence
* **output: pcr |** `list(int)`: pitch class representation of note(s) - integers in base 12

### function: key_signature_mapping
adds accidentals to a melody; maps a melody to its keymap 
* **input: music |** `str`: stripped and expanded music; output from expand_music
* **input: keymap |** `dict`: a key_length.song_key.keymap
* **output: converted |** `str`: music with accidentals to match the keymap

### class: pre_song
essentially a tune object from sjkabc. Called pre-song as it is a pre-pre-processing song before we use it. Has properties as defined by the header lines in abc content and song content that has not been modified.

### class: post_song
processed song with the information that we want for analysis
* **input: pre_song |** a `pre_song` object 
---
#### properties
* **pre |** `pre_song`: the pre_song version of the post_song
* **music |** `str`: the expanded and stripped abc version of the pre_song
* **given_key |** `key_length.song_key`: of the song
* **key_center |** `int`: the pitch class representation of the key of the given_key
* **default_keymap |** `dict`: the keymap of the given_key (`key_length.song_key.keymap`)
* **pitches |** `list`: all pitches in order of the song
* **durations |** `list`: all durations in order of the song
* **notelist |** `list(note.notes)`: list of note objects
* **transposed_pitches |** `list(int)`: `self.pitches` transposed to be centered around pitch class 0
* **total_duration |** `frac`: the sum of all durations in `self.durations`
---
#### methods
* **do_mapping |** returns string of `self.music` with added accidentals from the keymap
* **extract_notes |** sets attributes `self.pitches`, `self.durations`, and `self.notelist` 

## [dataset_creator](dataset_creator.py)
Preprocesses a set of abc notation songs from a directory and puts them into a data.csv file. 

### function: write_data
writes data into an output file
* **input: filepath |** str: filepath to the output file. Must be a csv file
* **input: inputs |** list(list): a list of lists ie a list of rows of data to add to the file
* **output: none**

### function: create_data_csv
creates the data.csv file containing all the preprocessed songs from a set of .txt or .abc files in a directory. The file contains rows of data of the format `'title', 'key_center', 'sum_dur', 'n_notes', '[p][d]'` where the length of `[p]` and `[d]` are each `n_notes`, and where the value of `n_notes` need not be the same for each row. 

* **input: data_directory |** str: the directory path with contains the files with the songs to add to the set
* **input: output_filename = `'data.csv'`|** str: the name of the file to output the data to. By default, this is `'data.csv` in `os.getcwd()`. 
* **output: none** | the data is written to the file

## [data_analyzer](data_analyzer.py)
Reads data from `data.csv` (generated by [dataset_creator](#dataset_creator), which contains information from a collection of post_song objects. Then, processes the data file by parsing into 144 subsets based on note-to-note transitions from the songs within the set and performs MLE for each set to define Beta distributions for the time-dependent transition matrix of a corpus of melodies. 

### function: fit_beta
Fits a dataset to a beta distribution using MLE (the default fit method) with location parameter = 0 and scale = 1 (ie. fits to beta within the default range of 0 to 1). 

* **input: vars |** `list`: list of values to fit the distribution to
* **output: results |** `tuple(float, float)`: tuple of $\alpha$, $\beta$ parameters for the beta distribution 

### function: read_data_file
Reads data from the `data.csv` file and converts each row into a row_obj object.

* **input: filename |** `str`: csv file of song data
* **output: songs |** `list(row_obj)` where each `row_obj` is as defined below


### function: create_analysis_sets
partitions data from all songs in a list of `row_obj` objects into 144 data sets to perform MLE on. 

* **input: rowlist |** `list(row_obj)`: a list of row objects from which to extract the data
* **output: set_mat |** `list(list(list(float))))`: a 12x12 matrix of data sets of relative time values (see [row_obj](#class-rowobj))

### function: create_distribution_matrix
creates a matrix of distribution objects from a matrix of parameters corresponding with the transition from pitch $i$ to pitch $j$ for each $i,j$the cell in a matrix of ($\alpha$, $\beta$) parameters for beta distributions.

* **input: beta_matrix |** `list(list(tuple(float)))`: a list of 12 lists, each inner list consists of 12 tuples as the parameters of a
    beta function theoretically created via an `data_analyzer.fit_beta()` function on a data set
* **output: mat |** `list(list(scipy.stats.beta.frozen))` 12x12 matrix of "frozen" distribution object with parameters from the input for each of the corresponding cells from the input 


### class: row_obj
A row object generated from a row from a csv file formatted in [dataset_creator](#datasetcreator) (generally, this is `data.csv`).

* **input: \*args |** a row from `data.csv` formatted according to the headers `['title', 'key_center', 'sum_dur', 'n_notes', '[p][d]']` as defined in [dataset_creator](#datasetcreator).
---
#### properties
* **title |** `str`: the title of the song
* **keycenter |** `int`: the keycenter of the song in pitch class notation (base 12)
* **total_duration |** `frac`: the sum of all durations in the song
* **nnotes |** `int`: the number of notes in the song
* **pitches |** `list(int)`: list of each of the C-centered pitches of notes in the song
* **durations |** `list(frac)`: list of each of the fractional durations of the notes in the song
* **xvals |** `list(float)`: list of the durations of each of the notes in the song relative to the whole duration of the song ($\forall x, 0< x << 1$)
* **times |** `list(float)`: list of the times at which each note occurs relative to the duration of the song ($\forall x, 0 < x < 1$)

### class: analysis_set
Object which performs analysis on a 12x12 matrix of data sets containing transition times (a matrix from the output of [create_analysis_sets](#function-createanalysissets))

* **input: data_list |** `list(list(list(float)))`: the output from [create_analysis_sets](#function-createanalysissets)
---
#### properties
* **set |** `list(list(list(float)))`: the raw input data
* **beta_fit |** `list(list(tuple(float)))`: 12x12 matrix of beta ($\alpha, \beta$) parameters for the MLE fit of a beta random variable to each of the input sets in `self.set`
* **beta_dist |** `list(list(beta))`: 12x12 matrix of frozen beta distribution objects with parameters from `self.beta_fit`

---
#### methods
* **fit_beta |** sets attributes `self.beta_fit` and `self.beta_dist`

