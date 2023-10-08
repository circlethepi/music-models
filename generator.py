import csv
import os
import ast
import data_analyzer as dr
import numpy as np
import scipy.stats as stats
import time

# import analyze_set as an

cwd = os.getcwd()


class generator:
    def __init__(self, fit_filename, data_filename):
        # reading fit data
        with open(cwd + "/" + fit_filename, "r") as f:
            reader = csv.reader(f)
            rowlist = list(reader)  # list of lists - inner have strings

        ##format back into list of lists
        fitmat = []
        for row in rowlist:
            fitrow = []
            for item in row:
                if item == 'n/a':
                    fitrow.append(item)
                else:
                    fitrow.append(ast.literal_eval(item))
            fitmat.append(fitrow)
        # print(fitmat)
        self.fitmat = fitmat
        #for row in fitmat:
        #    print(row)

        distmat = dr.create_distribution_matrix(fitmat)
        self.distmat = distmat

        # reading data matrix
        with open(cwd + "/" + data_filename, "r") as f:
            reader = csv.reader(f)
            rowlist = list(reader)  # list of lists - inner have strings

        ##format back into list of lists
        datamat = [[], [], [], [], [], [], [], [], [], [], [], []]
        for row in rowlist:
            for i in range(12):
                if row[i] == 'n/a':
                    datamat[i].append(row[i])
                else:
                    datamat[i].append(ast.literal_eval(row[i]))

        self.datamat = datamat


    # WORKS!!!
    def generate_transition_matrix(self, time, increment):
        """

        :param time: the time to evaluate the transition matrix - must be between 0 and 1
        :param increment: time increment to calculate probs in/ rel note length at note location
        :return: 12x12 matrix of transition probabilities at time
        """

        dist = self.distmat

        start = generate_cdf_matrix(dist, time)
        end = generate_cdf_matrix(dist, time + increment)

        out = []
        for i in range(12):
            add = normalize_row_diff(end[i], start[i])
            out.append(add)

        # Printing for Sanity Check
        # print('TRANSITION MATRIX AT ', time, "; with increment ", increment)
        # for i in range(12):
        #    print(out[i], sum(out[i]))

        return out

    # aug16'22 - works! fixed function defs in data_reader and streamlined cdf generation
    def generate_pitch_melody(self, start_pitch, total_notes):
        """

        :param start_pitch: integer value of starting pitch class for melody
        :param total_notes: total number of notes to be in melody
        :return:
        """

        distmat = self.distmat
        # for i in range(12):
        # print(self.distmat[i])

        # for i in range(12):
        # print(self.fitmat[0])

        increment = 1 / total_notes
        melody_pitches = [start_pitch]

        for t in range(1, total_notes):
            # situating ourselves in the melody
            current_time = increment * t

            next_time = increment * (t + 1)
            current_pitch = melody_pitches[t - 1]
            print('current pitch: ', current_pitch)

            # getting dist row for last pitch
            # pit_row = self.distmat[last_pitch]
            # print(pit_row)

            # getting row of transition probabilities
            cdf_current = generate_cdf_row(distmat, current_pitch, current_time)
            cdf_next = generate_cdf_row(distmat, current_pitch, next_time)

            transrow = normalize_row_diff(cdf_next, cdf_current)

            print("transition row for pitch ", current_pitch, "at time ", current_time, ":  ", transrow)
            # print("total prob of trans row probs = ", np.sum(transrow))
            next_pit = np.random.choice(range(12), 1, p=transrow)[0]

            print('next_pitch: ', next_pit)
            melody_pitches.append(next_pit)

            # print(melody_pitches)

        melody_pitches.append(0)
        print('final melody: ', melody_pitches)

        return melody_pitches

    def extract_model_analysis(self):
        distmat = self.distmat

        analysis_matrix_dict = {
            "q1": self.generate_transition_matrix(0.001, 0.25),
            "q2": self.generate_transition_matrix(0.25, 0.25),
            "q3": self.generate_transition_matrix(0.5, 0.25),
            "q4": self.generate_transition_matrix(0.75, 0.25),

            "beginning": self.generate_transition_matrix(0.001, 0.1),
            "ending": self.generate_transition_matrix(0.9, 0.1),

            "h1": self.generate_transition_matrix(0.001, 0.5),
            "h2": self.generate_transition_matrix(0.5, 0.5)
        }

        # create a dict of form       section: note: most likely transition, highest trans prob
        output_dict = {}
        for pair in analysis_matrix_dict.items():

            key = pair[0]
            mat = pair[1]

            # create a dict of form      pitch class: (most likely transition, highest trans prob)
            most_likely = {}
            count = 0
            for row in mat:
                most_likely[count] = (row.index(max(row)), max(row))
                count += 1

            output_dict[key] = most_likely

        for dict in output_dict.items():
            section = dict[0]
            notesdict = dict[1]

            print('Highest Probability Transitions by Note for ', section)
            print('PC \t\ttrans \t\t\ttransProb')
            for note in notesdict.items():
                # print(note)
                pc = note[0]
                trans = note[1][0]
                transProb = note[1][1]

                print(pc, "\t\t", trans, "\t\t\t", transProb)

    def do_kstest(self, data_points_filename, plvl, printres):
        """

        :param data_points_filename: csv filename containing data
        :param plvl: pval to test against
        :param print: boolean whether to print results
        :return: test stat matrix, pval matrix, test result matrix
        """
        # reading data matrix
        with open(cwd + "/" + data_points_filename, "r") as f:
            reader = csv.reader(f)
            rowlist = list(reader)  # list of lists - inner have strings

        ##format back into list of lists
        datamat = [[], [], [], [], [], [], [], [], [], [], [], []]
        for row in rowlist:
            for i in range(12):
                if row[i] == 'n/a':
                    datamat[i].append(row[i])
                else:
                    datamat[i].append(ast.literal_eval(row[i]))

        statmat = []
        pmat = []
        resmat = []
        for i in range(len(datamat)):
            statrow = []
            prow = []
            resrow = []
            for j in range(len(datamat[i])):

                testdist = self.fitmat[i][j]
                # print(testdist)

                if testdist == 'n/a':
                    statrow.append('NO TEST')
                    prow.append('NONE')
                    resrow.append('none')
                    pass
                else:
                    distmake = stats.beta(testdist[0], testdist[1])
                    #print(distmake)

                    stat, pval = stats.kstest(datamat[i][j], distmake.cdf, N=100000)#'beta', args=(testdist[0], testdist[1]))

                    statrow.append(stat)
                    prow.append(pval)

                    if pval < plvl:
                        resrow.append('REJECT')  # reject null that proposed dist is correct
                    else:
                        resrow.append('MATCH')  # cannot reject null and proposed dist is correct

            statmat.append(statrow)
            pmat.append(prow)
            resmat.append(resrow)

        if printres == True:
            # count reject/match/none values
            nc = 0
            mc = 0
            rc = 0
            for i in range(len(resmat)):
                for j in range(len(resmat[i])):
                    if resmat[i][j] == 'none':
                        nc += 1
                    elif resmat[i][j] == 'MATCH':
                        mc += 1
                    elif resmat[i][j] == 'REJECT':
                        rc += 1

            print('\n\nKOLMOGOROV-SMIRNOV TEST\n')
            for i in range(12):
                print(statmat[i])
            print('\n\np values for test\n')
            for i in range(12):
                print(pmat[i])
            print('\n\nTEST RESULTS for critical value', plvl, '\n')
            for i in range(12):
                print(resmat[i])

            print('Number of distributions REJECTED: ', rc)
            print('Number of distributions MATCHED: ', mc)
            print('Number of distributions nonexisted: ', nc)

        return statmat, pmat, resmat

    def do_sim_kstest(self, data_points_filename, plvl, nsims, printres):
        """

        :param data_points_filename: csv filename containing data set matrix
        :param plvl: p value below which we reject the null that the fits we found are good
        :param nsims: number of sims to do for each cell
        :param printres: boolean whether to print the results
        :return: pval matrix, results matrix
        """

        '''  SETUP   '''
        # we only care about statmat
        statmat, pmat, resmat = self.do_kstest(data_points_filename, plvl, False)
        # statmat are our actual test statistics

        # reading data matrix
        with open(cwd + "/" + data_points_filename, "r") as f:
            reader = csv.reader(f)
            rowlist = list(reader)  # list of lists - inner have strings

        ##format back into list of lists
        datamat = [[], [], [], [], [], [], [], [], [], [], [], []]
        for row in rowlist:
            for i in range(12):
                if row[i] == 'n/a':
                    datamat[i].append(row[i])
                else:
                    datamat[i].append(ast.literal_eval(row[i]))

        # create matrix of dataset sizes (might delete later)
        sizemat = []
        for i in range(len(datamat)):
            sizerow = []
            for j in range(len(datamat[i])):
                sizerow.append(len(datamat[i][j]))
            sizemat.append(sizerow)

        # running simulations test
        fits = self.fitmat

        ''' running simulations for each cell '''
        pvals = []
        results = []
        for i in range(len(statmat)):
            pvalrow = []
            resrow = []
            for j in range(len(statmat[i])):
                #print('cell: ', i, ',', j)
                #print(sizemat[i][j])
                # getting our actual test stat
                data_test_stat = statmat[i][j]

                if sizemat[i][j] < 10:
                    pvalrow.append('    NONE   ')
                    resrow.append('none')
                else:
                    ''' RUNNING ALL THE SIMULATIONS FOR THE CELL '''
                    sim_test_stats = []
                    for k in range(nsims + 1):
                        # generate simulated data from proposed dist
                        sim_data = stats.beta.rvs(fits[i][j][0], fits[i][j][1], size=sizemat[i][j])
                        # print(fits[i][j][0], fits[i][j][1])

                        # get estimated params from sim
                        te = time.time()   #getting runtime for sampling
                        a, b, loc, scale = stats.beta.fit(sim_data, fits[i][j][0], fits[i][j][1])
                        sim_params = (a, b)
                        # print(sim_params[0], sim_params[1])


                        #printing time thigns
                        tep = time.time() - te
                        print('time for sample: ', tep)


                        #again
                        te = time.time()

                        # get dist from sim
                        sim_dist = stats.beta(sim_params[0], sim_params[1])

                        # perform KS test with sim data on sim dist
                        sim_stat, simp = stats.kstest(sim_data, sim_dist.cdf)

                        # add sim_stat to list from set of sims
                        sim_test_stats.append(sim_stat)

                                #printing time things
                        tep = time.time() - te
                        print('time for test: ', tep)

                    # getting proportion of test stats bigger than our actual test stat from data
                    n_bigger = sum(l > data_test_stat for l in sim_test_stats)
                    pval = float(n_bigger / nsims)

                    # adding our pval to the table
                    pvalrow.append(pval)

                    if pval < plvl:
                        resrow.append('REJECT NULL')
                    elif pval >= plvl:
                        resrow.append('FAIL TO REJ')

            pvals.append(pvalrow)
            results.append(resrow)

        if printres == True:
            # count reject/match/none values
            nc = 0
            mc = 0
            rc = 0
            for i in range(len(resmat)):
                for j in range(len(resmat[i])):
                    if resmat[i][j] == '    NONE   ':
                        nc += 1
                    elif resmat[i][j] == 'FAIL TO REJ':
                        mc += 1
                    elif resmat[i][j] == 'REJECT NULL':
                        rc += 1

            print('pvalues from test\n')
            for i in range(12):
                print(pvals[i])
            print('\n\nTEST RESULTS for critical value: ', plvl, '\n')
            for i in range(12):
                print(results[i])

            print('Number of distributions REJECTED H0: ', rc)
            print('Number of distributions FAILED TO REJECT H0: ', mc)
            print('Number of distributions unable to test: ', nc, '\n\n')


######################################################
#                OTHER FUNCTIONS
######################################################
def generate_cdf_row(distmat, pitch, time):
    """

    :param distmat: 12x12 distribution matrix to use
    :param pitch: pitch to generate row for; integer between 0 and 11 inclusive
    :param time: time at which to take cdf
    :return: row of cdf values for pitch at time
    """

    distrow = distmat[pitch]

    outrow = []

    for i in range(12):
        cd = distrow[i]
        if cd == 0:
            val = 0
        else:
            val = cd.cdf(time)

        outrow.append(val)

    return outrow


def normalize_row_diff(end, start):
    """

    :param end: cdf row at end time (list of len 12)
    :param start: cdf row at start time (list of len 12)
    :return: normalized row for the increment between times so that row probability is 1

    """

    diff = []
    for i in range(12):
        diff.append(end[i] - start[i])

    scale = sum(diff)

    out = []
    for i in range(12):
        add = diff[i] / scale
        out.append(add)

    return out


def generate_cdf_matrix(distmat, time):
    '''
    generates 12x12 cdf matrix at input time

    :param distmat: 12x12 distribution matrix to get from
    :param time: time at which to take cdf
    :return: 12x12 cdf matrix at input time
    '''

    mat = []

    for i in range(12):
        row = generate_cdf_row(distmat, i, time)
        mat.append(row)

    # print('cdf matrix at ', time)
    # for i in mat:
    #    print(i, sum(i))

    return mat
