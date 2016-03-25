import os
import sys
import numpy as np
import caffe
import argparse


parser = argparse.ArgumentParser(description='Computes 5-fold cross-validation results over Twitter five-agrees dataset')
parser.add_argument('-ov', '--oversampling', help='Enables (1) or disables (0) oversampling')
args = parser.parse_args()

if args.oversampling == 0:
    oversampling = False
elif args.oversampling == 1:
    oversampling = True
else:
    sys.exit("oversampling must be 0 or 1")

subsets = ['test1', 'test2', 'test3', 'test4', 'test5']
mean_file = 'ilsvrc_2012_mean.npy'
#mean_file = 'places205CNN_mean.npy'
accuracies = []
output_string = ""

for subset in subsets:
    # Update paths for this subset
    deploy_path = 'sentiment_deploy.prototxt'
    caffemodel_path = 'twitter_finetuned_' + subset + '_iter_180.caffemodel'
    ground_truth = 'ground_truth/' + subset + '/test.txt'
    instanceList = []
    correctLabels = 0
    incorrectLabels = 0
    positiveLabels = 0
    negativeLabels = 0
    positivePredictions = 0
    negativePredictions = 0

    gt_file = open(ground_truth, "r")

    # Store images in a list
    while (True):
        line = gt_file.readline()
        # Check if we have reached the end
        if (len(line) == 0):
            break
        # Add the line to the list
        instanceList.append(line)

    # Load network
    net = caffe.Classifier(deploy_path,
                           caffemodel_path,
                           mean=np.load(mean_file).mean(1).mean(1),
                           image_dims=(256, 256),
                           channel_swap=(2, 1, 0),
                           raw_scale=255)

    # Loop through the ground truth file, predict each image's label and store the wrong ones
    counter = 0
    for instance in instanceList:
        values = instance.split()
        image_path = values[0]
        sentiment = int(values[1])

        # Load image
        im = caffe.io.load_image(image_path)

        # Make a forward pass and get the score
        prediction = net.predict([im], oversample=oversampling)

        # Check if the prediction was correct or not
        if prediction[0].argmax() == sentiment:
            correctLabels += 1
        else:
            incorrectLabels += 1

        # Update label counter
        if sentiment == 0:
            negativeLabels += 1
        else:
            positiveLabels += 1

        # Update prediction counter (negative = 0, positive = 1)
        if prediction[0].argmax() == 0:
            negativePredictions += 1
        else:
            positivePredictions += 1

        counter += 1
        if counter % 40 == 0:
            print subset + ', ' + str(counter)
            sys.stdout.flush()

    gt_file.close()
    accuracy = 100. * correctLabels / (correctLabels + incorrectLabels)
    accuracies.append(accuracy)

    # Print accuracy results
    print '------------- ' + subset + ' -------------'
    print 'Accuracy = ', str(accuracy)
    print '---------------------------------'

    output_string += 'Subset: {0}: \n    Positive images: {1}\n    Negative images: {2}\n    Positive predictions: {3}\n    Negative predictions: {4}\n'.format(
        subset, str(positiveLabels), str(negativeLabels), str(positivePredictions), str(negativePredictions))

print '\nRESULTS:'
for i in range(0, 5):
    print subsets[i] + ': ' + str(accuracies[i]) + '%'
print '\nMean accuracy = ' + str(1. * sum(accuracies) / len(accuracies))
print "\n-------------------------------------\n"
print output_string
