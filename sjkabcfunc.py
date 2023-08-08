##functions from SJKABC
import textwrap
import song_processer as ps
HEADER_KEYS = dict(
    B='book',
    C='composer',
    D='discography',
    F='file',
    G='group',
    H='history',
    I='instruction',
    K='key',
    L='note_length',
    M='metre',
    N='notes',
    O='origin',
    P='parts',
    Q='tempo',
    R='rhythm',
    S='source',
    T='title',
    X='index',
    Z='transcription'
)

def get_id_from_field(field):
    """Get id char from field name

    :param str field: 'long' name of field, for example 'title'
    :returns: id character, for example 'T'
    :rtype: str
    :raises KeyError: if key does not exist.

    """
    for key in HEADER_KEYS:
        if HEADER_KEYS[key] == field:
            return key
    else:
        raise KeyError('No such header key: {}'.format(field))


def get_field_from_id(id):
    """Get long field name from id char.

    :param str id: id char, for example 'T'
    :returns: long field name, like 'title'
    :rtype: str
    :raises KeyError: if key does not exist.

    """
    try:
        return HEADER_KEYS[id]
    except KeyError:
        raise KeyError('No such header key: {}'.format(id))


def wrap_line(string, id, max_length=78, prefix='+'):
    """
    Wrap header line.

    :param str string: string to wrap
    :param str id: character id of header line
    :param int max_length: maximum line length
    :param str prefix: Line prefix for wrapped lines (first line exempted)
    :returns: wrapped line
    :rtype: str

    .. seealso:: :func:`get_id_from_field`
    """
    w = textwrap.TextWrapper()
    w.initial_indent = '{}:'.format(id)
    w.subsequent_indent = '{}:'.format(prefix)
    w.width = max_length
    return '\n'.join(w.wrap(string))

def expand_repeats(abc):
    """
    Expand repeats with support for (two) alternate endings.

    Example::

        >>> print(expand_repeats('aaa|bbb|1ccc:|2ddd|]'))
        aaa|bbb|ccc|aaa|bbb|ddd|

    :param str abc: abc to expand
    :returns: expanded abc
    :rtype: str

    """
    parsed_abc = abc
    start = 0
    end = 0

    parsed_abc = parsed_abc.replace('::', ':||:')
    parsed_abc = parsed_abc.replace(':|:', ':||:')

    while True:
        end = parsed_abc.find(':|', start)
        if (end == -1):
            break

        new_start = parsed_abc.rfind('|:', 0, end)
        if (new_start != -1):
            start = new_start+2

        tmp = []
        if end + 2 < len(parsed_abc) and parsed_abc[end+2].isdigit():
            first_ending_start = parsed_abc.rfind('|', 0, end)
            num_bars = 1
            if not parsed_abc[first_ending_start+1].isdigit():
                first_ending_start = parsed_abc.rfind('|', 0,
                                                      first_ending_start)
                num_bars = 2

            tmp.append(parsed_abc[start:first_ending_start])
            tmp.append('|')
            tmp.append(parsed_abc[first_ending_start+2:end])
            tmp.append('|')

            second_ending_start = end+2
            second_ending_end = None
            for i in range(num_bars):
                second_ending_end = parsed_abc.find('|', second_ending_start)

            tmp.append(parsed_abc[start:first_ending_start])
            tmp.append('|')
            tmp.append(parsed_abc[second_ending_start+1:second_ending_end])
            parsed_abc = parsed_abc.replace(
                parsed_abc[start:second_ending_end],
                ''.join(tmp), 1)
            start += len(tmp)
        else:
            tmp.append(parsed_abc[start:end])
            tmp.append('|')
            tmp.append(parsed_abc[start:end])
            tmp.append('|')
            parsed_abc = parsed_abc.replace(parsed_abc[start:end+2],
                                            ''.join(tmp), 1)
            start += len(tmp)

    for rep in ['|:', ']']:
        parsed_abc = parsed_abc.replace(rep, '')
    parsed_abc = parsed_abc.replace('||', '|')

    return parsed_abc


def strip_chords(abc):
    """Strip chords and 'guitar chords' from string.

    Example::

        >>> #from sjkabc import strip_chords
        >>> stripped = strip_chords('"G" abc|"Em" bcd|[GBd] cde')
        >>> stripped
        ' abc| bcd | cde'

    :param str abc: abc to filter
    :returns: abc with chords stripped
    :rtype: str

    """
    ret = []
    in_chord = False

    for c in abc:
        if c == '[' or (c == '"' and not in_chord):
            in_chord = True
        elif c == ']' or (c == '"' and in_chord):
            in_chord = False
        elif in_chord:
            continue
        else:
            ret.append(c)

    return ''.join(ret)

#modified to not get rid of slashes since this will affect the rhythm
def strip_extra_chars(abc):
    """Strip misc extra chars (/\<>)

    :param str abc: abc to filter
    :returns: filtered abc
    :rtype: str

    """
    for rep in '<,>\[\']':
        abc = abc.replace(rep, '')
    return abc





##PARSER
class Parser:

    """
    This class provides iterable parsing capabilities.

    `Parser` must be initialised with a string containing ABC music
    notation. This class is iterable and will return a `Tune` object
    for every tune found in the provided ABC notation.

    Example::

        >>> for tune in Parser(abc):
        ...     print('Parsed ', tune.title)

    .. seealso:: :class:`Tune`
    """

    def __init__(self, abc=None):
        """Initialise Parser

        :param abc: string containing ABC to parse

        """
        self.tunes = []
        self.last_field = None

        if abc:
            self.parse(abc)
        self.index = len(self.tunes)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.tunes[self.index]

    def parse(self, abc):
        """Parse ABC notation.

        This function will append found ABC tunes to `self.tunes`.

        :param abc: string containing abc to parse

        """
        in_header = False
        current_tune = None

        for line in abc.splitlines():
            if self._line_empty(line) or self._line_comment(line):
                continue

            # At beginning of header
            if self._line_is_index(line):
                if current_tune:
                    # We have a parsed tune already, append it to list of
                    # tunes.
                    self.tunes.append(current_tune)

                in_header = True
                current_tune = ps.pre_song()

            if in_header:
                (key, val) = line.split(':', 1)
                if key in HEADER_KEYS:
                    getattr(current_tune, HEADER_KEYS[key]).append(val.strip())
                    self.last_field = HEADER_KEYS[key]

                # Continuation of info field.
                if key == '+' and self.last_field:
                    field = getattr(current_tune, self.last_field)
                    field[-1] = field[-1] + ' ' + val.strip()

                # Header ends at K:
                if self._line_is_key(line):
                    in_header = False

            else:
                if current_tune:
                    current_tune.abc.append(line)

        else:
            if current_tune:
                self.tunes.append(current_tune)

    def _line_is_key(self, line):
        """Check if line is a K: line

        :param str line: line to check
        :returns: True if line is a key line and False if not.
        :rtype: bool

        """
        if line.startswith('K:'):
            return True
        else:
            return False

    def _line_empty(self, line):
        """Check if line is empty

        :param str line: line to check
        :returns: True if line is empty and False if not.
        :rtype: bool

        """
        line = line.strip()
        if line == '':
            return True
        else:
            return False

    def _line_comment(self, line):
        """Check if line is a comment

        :param str line: line to check
        :returns: True if line is a comment and False if not.
        :rtype: bool

        """
        line = line.strip()
        if line.startswith('%'):
            return True
        else:
            return False

    def _line_is_index(self, line):
        """Check if line is an index line (X:).

        If it is, it is considered to be the start of a tune.

        :param str line: line to check
        :returns: True if line is a index line, False if not.
        :rtype: bool

        """
        if line.startswith('X:'):
            return True
        else:
            return False

    def _line_is_continued_line(self, line):
        """Check if line is a continuation of the last

        :param str line: Line to check
        :returns: true if the line is a continuation line

        """
        if line.startswith('+:'):
            return True
        else:
            return False