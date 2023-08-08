import sjkabcfunc as sjk
from fractions import Fraction as frac

##
class song_div :
    def __init__(self, leninfo, timeinfo):
        if leninfo == []:
            slash = False
            d = []
            for c in str(timeinfo):
                if c == '/':
                    slash = True
                elif slash and c in '1234567890':
                    d.append(c)
            self.default_length = frac(''.join(['1/', ''.join(d)]))
            #self.default_length = frac(''.join(['1/', str(timeinfo)[2]]))
        else:
            self.default_length = frac(leninfo[0])




#order of accidentals added
flat_order = ['B', 'E', 'A', 'D', 'G', 'C', 'F']
sharp_order = ['F', 'C', 'G', 'D', 'A', 'E', 'B']
#transposition from relative major in half steps for each mode
mode_transposition = {'major': 0, 'minor': 3, 'mixolydian': -7, 'dorian': -2, 'phrygian': -4, 'lydian': -5, 'locrian': 1}


#number of sharps or flats for each major key center
number_accidentals = {'C#': 7, 'F#': 6, 'B': 5, 'E': 4, 'A': 3, 'D': 2, 'G': 1, 'C': 0, 'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6, 'Cb': -7}

#note transpositions
pitch_values = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11, 'Z':13}
accidental_values = {'=': 0, '^': 1, '_': -1}
chromatic_notes = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


class song_key:
    def __init__(self, keyinfo):
        self.key_raw = keyinfo

    @property
    def keymode(key):  # MO may 22
        """
        finds and returns the keymode that we are working with
        :param key: string of key def from abc header
        :return: scale type (one of the seven modes)
        """

        if "DOR" in key.key_raw.upper():
            return "dorian"
        elif "PHR" in key.key_raw.upper():
            return "phrygian"
        elif "LYD" in key.key_raw.upper():
            return "lydian"
        elif "MIX" in key.key_raw.upper():
            return "mixolydian"
        elif "LOC" in key.key_raw.upper():
            return "locrian"
        elif "M" in key.key_raw.upper():
            return "minor"
        else:
            return "major"

    @property
    def keycenter(key):  # MO May 22
        """
        finds the key center
        :param key: string of key from abc header
        :return: key center string (accidental)(note name)

        ex: Key is G# minor
        returns ^G
        """

        ret = ['x','x']
        if 1 < len(key.key_raw):
            if key.key_raw[1] != ('b' or '#'):
                ret[0] = '='
                ret[1] = key.key_raw[0]
            else:
                for c in key.key_raw[0:2]:
                    if c in 'ABCDEFG':
                        ret[1] = c
                    elif c == 'b':
                        ret[0] = '_'
                    elif c == '#':
                        ret[0] = '^'
        else:
            ret[0] = '='
            ret[1] = key.key_raw[0]
        return ''.join(ret)

    @property
    def relative_major(key):
        """

        :return: integer pitch class number of relative major key
        """
        transp_from_maj = mode_transposition[key.keymode]

        pitchval = pitch_values[key.keycenter[1].upper()]
        accval = 0
        if 1 < len(key.keycenter):
            accval = accidental_values[key.keycenter[0]]
        relmaj = (pitchval + accval + transp_from_maj) % 12
        return relmaj

    @property
    def keymap(key):  # MO may 22
        """
        this mapping ignores modified keys as the corpus does not contain any tunes with modified keys.

        :param key: key definition ex: Gm, Gmixolidian, Bb
        :return: keymapping to translate letters into absolute pitches from map
        """
        # set default keymap
        keymap = {'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G', ' ': ' ', 'Z': 'Z'}

        rel_major = key.relative_major  # set relative major number
        rel_major_name = chromatic_notes[rel_major]  # get relative major notename
        accidentals = number_accidentals[rel_major_name]  # get number of accidentals in relative major
        # print(rel_major_name, "\n", accidentals) #sanity check

        # if sharp key
        if accidentals > 0:
            for i in range(accidentals):
                keymap[sharp_order[i]] = "^" + keymap[sharp_order[i]]
        else:
            for i in range(-accidentals):
                keymap[flat_order[i]] = "_" + keymap[flat_order[i]]

        return keymap




#
#
