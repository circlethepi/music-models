import csv
from fractions import Fraction as frac
from scipy.stats import beta
import dataset_creator as dc

"""
reads data from data.csv containing information from post_song objects (data.csv is generated in dataset_creator)

processes the data file by parsing into 144 subsets based on note-to-note transitions from the songs contained within 
the data set and performs MLE to the set to define Beta distributions for the time-dependent transition matrix of a 
corpus of melodies.

"""

def fit_beta(vars):
    """
    fits a dataset to a beta distribution using MLE (the default fit method) with location parameter = 0 and scale = 1
    ie fits to beta within the default range of 0 to 1

    :param vars: list | list of values to fit to the distribution

    :return results: tuple | (alpha, beta) parameters of the MLE fitting
    """
    a1, b1, loc1, scale1 = beta.fit(vars, floc=0, scale=1)
    #print(a1, b1)
    results = (a1, b1)
    return results


def read_data_file(filename):
    """
    reads data from the data.csv file and converts each row into a row_obj object

    :param filename: str | csv file of song data
    :return songs: list(row) where each row is the post_song data for each song in the file
    """
    songs = []
    with open(filename, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != None:
            for row in reader:
                songs.append(row_obj(row))

    return songs


class row_obj:
    """
    row object generated from a row from csv file formatted from dataset_creator
    """
    def __init__(self, *args):

        #take just the list of input arguments
        args = args[0]
        title = args[0] #getting title from first field
        keycenter = int(args[1]) #getting keycenter from second field
        sum_dur = frac(args[2]) #getting the total duration from third field
        nnotes = int(args[3]) #getting total number of notes from fourth field

        #print(title, keycenter, sum_dur, nnotes)

        #setting attributes from this info
        self.title = title
        self.keycenter = keycenter
        self.total_duration = sum_dur
        self.nnotes = nnotes

        #pitch and duration list containers
        p = []
        d= []

        #filling in containers with normalized duration
        for i in range(nnotes) :
            p.append(int(args[i+4]))
            d.append(frac(args[i+4+nnotes]))
        x = [d / sum_dur for d in d]

        #times at which pitches happen container
        exes = []
        for moment in range(1, len(x)+1):
            upto_now = sum(x[0:moment]) #sum durations up to current moment
            exes.append(upto_now)

        self.pitches = p
        self.durations = d
        self.xvals = x    #absolute durations
        self.times = exes  #"x values" in beta - the "timestamp" of the end of each note


def create_analysis_sets(rowlist):
    """
    will need to input songs into this function (generated in read_data_file) - or merge these two functions in the future
    :param rowlist: list(row_obj) | a list of row objects containing information about each song
    :return set_mat: analysis sets to do MLE to. a 12x12 matrix of list(list)
    """
    set_mat = [[[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]],
               [[],[],[],[],[],[],[],[],[],[],[],[]]]
    #set_mat=[]

    for row in rowlist:
        for i in range(12):
            for j in range(12):
                #set = []
                for n in range(1, row.nnotes):
                    if row.pitches[n] == j and row.pitches[n-1] == i:
                        set_mat[i][j].append(float(row.times[n]))
                #set_mat[i].insert(j, set)

    #for i in set_mat:
    #    print(i)
    return set_mat


def create_distribution_matrix(beta_matrix):
    """
    crates a matrix of distribution objects from a matrix of parameters corresponding with the transition fron pitch i
    to pitch j for each i,jth cell in the matrix.

    :param beta_matrix: list(list) - a list of 12 lists, each inner list consists of 12 tuples as the paramaters of a
    beta function theoretically created via an analysis_set.fit_beta() function on a data set

    :return: mat: list(list) - a list of 12 lists, each inner list consisiting of 12 distribution objects
    """

    mat = [[],[],[],[],[],[],[],[],[],[],[],[]]
    for i in range(12):
        #nna = 0     #set number of n/as in row

        for j in range(12):
            if beta_matrix[i][j] == 'n/a':  #if n/a
                mat[i].append(0)            #set dist = 0
            else:                           #otherwise
                mat[i].append(beta(beta_matrix[i][j][0], beta_matrix[i][j][1]))     #put in the beta dist

    return mat


class analysis_set:
    """
    data_list is a set_mat returned from create_analysis_set

    """
    def __init__(self, data_list):
        self.set = data_list
        # writes the data into a csv
        dc.write_data('a_set.csv', data_list)
        #for i in fits:
        #    print(i)

    def trans_size(self):
        for i in self.set:
            for j in i:
                print(len(j))


    def fit_beta(self):
        fits = [[],[],[],[],[],[],[],[],[],[],[],[]]

        ##running beta mle on sets with samples
        for i in range(12):
            for j in range(12):
                current_set = self.set[i][j]
                if len(current_set):
                    mle = fit_beta(current_set)
                    fits[i].append(mle)
                else:
                    #if transition did not occur, input "n/a" instead of dist params
                    fits[i].append('n/a')

        #fits is the resulting matrix
        self.beta_fit = fits
        dc.write_data('a_fit.csv', fits)

        #creating dists based on the fits
        self.beta_dist = create_distribution_matrix(fits)
        dc.write_data('a_dist.csv', self.beta_dist)
        for i in fits:
            print(i)