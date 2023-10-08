# Importing everything
import data_analyzer as dz
import dataset_creator as dsc
import generator as gen

'''
EXECUTING EVERYTHING
Here, everything is executed in one file. This library is set up so that the preprocessing, analysis, and generative stages can be completed independently of one another (hence the reading and writing from data files). 

For ease of use, this file is set up so that you can change the controller names at the beginning of the file as desired. The default values will reproduce the results from the accompanying paper.
'''

data_dir = 'raw_data_files'
data_csv = 'example_outputs/data.csv'
sets_csv = 'example_outputs/sets.csv'
fit_csv = 'example_outputs/fit.csv'
dist_csv = 'example_outputs/dist.csv'




''' Processing & Analyzing Data to Create Model '''
# creating data csv from raw ABC files
#dsc.create_data_csv(data_directory=data_dir,
#                   output_filename=data_csv)

# converts pre-processed data into a set of objects
#song_list = dz.read_data_file(filename=data_csv)

# object which has partitioned the pre-processed data and will perform the fitting
#analysis_set_obj = dz.analysis_set(dz.create_analysis_sets(song_list),
#                                   set_csv_filename=sets_csv)

# creating the fits and writing the data
#analysis_set_obj.fit_beta(fit_file=fit_csv,
#                          beta_file=dist_csv)
    # fit.csv has the fit parameters
    # dist.csv has info for frozen beta rvs
    # .fits is the object of fits for each set
    # .beta_dist is the object of distributions



''' Corpus Analysis & Generation via Model '''
model_obj = gen.generator(fit_filename=fit_csv,
                          data_filename=sets_csv)

# model analysis
model_obj.extract_model_analysis()

# significance testing
model_obj.do_kstest(data_csv, 0.05, True)
model_obj.do_sim_kstest(data_csv, 0.05, 1000, True)

# generate melodies
model_obj.generate_pitch_melody(0, 50)








