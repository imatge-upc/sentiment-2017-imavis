# Based on code from https://www.kaggle.com/c/datasciencebowl/forums/t/12838/caffe-training-curves/90402


import os
import sys
import numpy as np

import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import math
import pylab
import sys
import argparse
import re
from pylab import figure, show, legend, ylabel

from mpl_toolkits.axes_grid1 import host_subplot

colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

all_training_losses = []
all_training_accuracies = []
all_validation_losses = []
all_validation_accuracies = []
all_training_iterations = []
all_validation_iterations = []

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description='Makes a plot from Caffe output')
  parser.add_argument('-o', '--output_path', help='folder where the generated plots will be stored')
  parser.add_argument('-p', '--output_files_prefix', help='prefix for the output files')
  parser.add_argument('-f','--files', nargs='+', help='List of training logs to plot (separated by blank spaces)', required=True)
  parser.add_argument('-m','--models', nargs='+', help='List with the names of the models (used for the legend of the graphs)', required=True)
  args = parser.parse_args()

  file_list = args.files #[str(item) for item in args.files.split(' ')]
  models_list = args.models #[str(item) for item in args.models.split(' ')]

  if len(models_list) > 4:
    ncols_ind = 2
  else:
    ncols_ind = 1

  output_path = args.output_path
  if output_path[-1] != '/':
    output_path = output_path + '/'
  
  for training_log in file_list:
    f = open(training_log, 'r')

    training_iterations = []
    training_loss = []
    training_accuracy = []

    test_iterations = []
    test_accuracy = []
    test_loss = []

    for line in f:

      if '] Iteration ' in line and 'loss = ' in line:
        arr = re.findall(r'ion \b\d+\b,', line)
        training_iterations.append(int(arr[0].strip(',')[4:]))

      if '] Iteration ' in line and 'Testing net' in line:
        arr = re.findall(r'ion \b\d+\b,', line)
        test_iterations.append(int(arr[0].strip(',')[4:]))
        #check_test = True

      if 'Test net output' in line and 'loss' in line:
        test_loss.append(float(line.strip().split(' ')[-2]))

      if 'Test net output' in line and 'accuracy' in line:
        test_accuracy.append(float(line.strip().split(' ')[-1]))

      if 'Train net output' in line and 'loss' in line:
        training_loss.append(float(line.strip().split(' ')[-2]))

      if 'Train net output' in line and 'accuracy' in line:
        training_accuracy.append(float(line.strip().split(' ')[-1]))

    print 'train iterations len: ', len(training_iterations)
    print 'train loss len: ', len(training_loss)
    print 'train accuracy len: ', len(training_accuracy)
    print 'test loss len: ', len(test_loss)
    print 'test iterations len: ', len(test_iterations)
    print 'test accuracy len: ', len(test_accuracy)

    if len(training_iterations) != len(training_accuracy): #awaiting test...
      print 'mis-match (training)'
      print len(training_iterations[0:-1])
      training_iterations = training_iterations[0:-1]
      test_iterations = test_iterations[0:-1]
      test_accuracy = test_accuracy[0:-1]
      test_loss = test_loss[0:-1]

    f.close()

    all_training_iterations.append(training_iterations)
    all_validation_iterations.append(test_iterations)
    all_validation_accuracies.append(test_accuracy)
    all_training_accuracies.append(training_accuracy)
    all_validation_losses.append(test_loss)
    all_training_losses.append(training_loss)
  

  # Plot loss
  host = host_subplot(111)#, axes_class=AA.Axes)
  #plt.subplots_adjust(right=0.75)

  host.set_xlabel("Iterations")
  host.set_ylabel("Loss")
 
  for (i, training_loss) in enumerate(all_training_losses):
    if len(training_loss) > 0:
      host.plot(all_training_iterations[i], training_loss, colors[i%len(colors)], label=models_list[i] + " (training)")
  for (i, test_loss) in enumerate(all_validation_losses):
    if len(test_loss) > 0:
      host.plot(all_validation_iterations[i], test_loss, colors[i%len(colors)]+'--', label=models_list[i] + " (validation)")

  host.legend(loc=1, prop={'size':12}, ncol=ncols_ind)

  plt.draw()
  plt.show()

  plt.savefig(output_path + args.output_files_prefix + '_loss.png')



  # Plot accuracy
  plt.clf()
  host = host_subplot(111)

  host.set_xlabel("Iterations")
  host.set_ylabel("Accuracy")
 
  for (i, training_accuracy) in enumerate(all_training_accuracies):
    if len(training_accuracy) > 0:
      host.plot(all_training_iterations[i], training_accuracy, colors[i%len(colors)], label=models_list[i] + " (training)")
  for (i, test_accuracy) in enumerate(all_validation_accuracies):
    if len(test_accuracy) > 0:
      host.plot(all_validation_iterations[i], test_accuracy, colors[i%len(colors)]+'--', label=models_list[i] + " (validation)")

  host.legend(loc=4, prop={'size':12}, ncol=ncols_ind)

  plt.draw()
  plt.show()

  plt.savefig(output_path + args.output_files_prefix + '_accuracy.png')


  # Plot accuracy+loss
  plt.clf()  # clear the previous plot
  host = host_subplot(111)
  plt.subplots_adjust(right=0.75)

  par1 = host.twinx()

  host.set_xlabel("Iterations")
  host.set_ylabel("Loss")
  par1.set_ylabel("Accuracy")
 

  ncol = 0
  for (i, training_loss) in enumerate(all_training_losses):
    if len(training_loss) > 0:
      host.plot(all_training_iterations[i], training_loss, colors[i%len(colors)], label=models_list[i] + "\nloss (training)")
      ncol += 1
  for (i, test_loss) in enumerate(all_validation_losses):
    if len(test_loss) > 0:
      host.plot(all_validation_iterations[i], test_loss,  colors[i%len(colors)]+'--', label=models_list[i] + "\nloss (validation)")
      ncol += 1
  for (i, training_accuracy) in enumerate(all_training_accuracies):
    if len(training_accuracy) > 0:
      par1.plot(all_training_iterations[i], training_accuracy, colors[i%len(colors)]+'-.', label=models_list[i] + "\naccuracy (training)")
      ncol += 1
  for (i, test_accuracy) in enumerate(all_validation_accuracies):
    if len(test_accuracy) > 0:
      par1.plot(all_validation_iterations[i], test_accuracy, colors[i%len(colors)]+':', label=models_list[i] + "\naccuracy (validation)")
      ncol += 1

  # Shrink current axis by 20%
  box = host.get_position()
  host.set_position([box.x0, box.y0, box.width * 0.8, box.height])

  # Put a legend to the right of the current axis
  host.legend(loc='center left', bbox_to_anchor=(1.15, 0.5), prop={'size':10})

  plt.draw()
  plt.show()

  plt.savefig(output_path + args.output_files_prefix + '_both.png')