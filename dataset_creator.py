import sjkabcfunc as sjk
import song_processor as ps
import csv
import os

"""
Pre-processes a set of abc notation songs and puts them into a data.csv file
"""


def write_data(filepath, inputs):
    """
    writes input rows to an output file
    ##writes input rows to the data.csv output file

    :param filepath: str | filepath to the output file ( a csv file )
    :param inputs: list of lists ie list[rows]
    :return: none
    """
    with open(filepath, 'w', newline='') as c:
        writer = csv.writer(c)
        writer.writerows(inputs)


def create_data_csv(data_directory, output_filename='data.csv'):
   """
   creates the data.csv file containing all the pre-processed songs from a set of .txt or .abc files.

   :param data_directory: str | the directory which contains the files with songs to add to the set
   :param output_filename: str | the name of the file to output to. Must be a .csv file

   :return:
   """

   cwd = os.getcwd()
   output_filepath = cwd + '/' + output_filename
   # setting up the content to go into the csv file
   header = ['title', 'key_center', 'sum_dur', 'n_notes', '[p][d]']
   rows = [header]

   # extracting the content from the files
   for dirpath, dirnames, filenames in os.walk(data_directory):

      # adding files with the correct extensions to the list of files to parse
      files = []
      for f in filenames:
         if f.endswith('.abc') or f.endswith('.txt'):
            files.append(f)

      # reading each of the files and extracting tunes
      for file in files:
         filepath = os.path.join(dirpath, file)

         # getting the content from the file
         with open(filepath, "r") as f:
            content = f.read()

         # getting tunes from the content
         for tune in sjk.Parser(content):
            # create a post_song object for each tune
            new = ps.post_song(tune)
            print(new.pre.title)
            new.extract_notes()  # have pitches, durations caluculated

            row = [tune.title[0], new.key_center, new.total_duration, len(new.notelist)]

            for p in new.transposed_pitches:
               row.append(p)
            # row.append(new.transposed_pitches)

            for d in new.durations:
               row.append(d)
            # row.append(new.durations)
            rows.append(row)

   # writing the data
   write_data(output_filepath, rows)

   return
