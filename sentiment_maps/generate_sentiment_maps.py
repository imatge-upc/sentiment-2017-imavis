import sys
import argparse
import numpy as np
import caffe


parser = argparse.ArgumentParser(description='Generate sentiment maps for the Twitter five-agrees dataset')
parser.add_argument('-o', '--output_path', help='folder where the generated sentiment maps will be stored')

args = parser.parse_args()
output_path = args.output_path

if output_folder[-1] != '/':
    output_folder += '/'

subsets = ['test1','test2','test3','test4','test5']
mean_file = 'ilsvrc_2012_mean.npy'

for subset in subsets:
    deploy_path = 'sentiment_fully_conv_deploy.prototxt'
    caffemodel_path = 'twitter_finetuned_'+subset+'_iter_180_conv.caffemodel'
    gt_file = '../ground_truth/five_agrees/'+subset+'/test.txt'

    file = open(gt_file,"r")

    # Store images in a list
    instanceList = []
    while(True):
        line = file.readline()
        # Check if we have reached the end
        if (len(line)==0):
            break
        # Add the line to the list
        instanceList.append(line)

    # Load fully convolutional network
    net_full_conv = caffe.Net(deploy_path, caffemodel_path, caffe.TEST)

    # Configure preprocessing
    transformer = caffe.io.Transformer({'data': net_full_conv.blobs['data'].data.shape})
    transformer.set_mean('data', np.load(mean_file).mean(1).mean(1))
    transformer.set_transpose('data', (2,0,1))
    transformer.set_channel_swap('data', (2,1,0))
    transformer.set_raw_scale('data', 255.0)

    # Loop through the ground truth file, predict each image's label and store the wrong ones
    for instance in instanceList:
        # Get path and ground truth
        values = instance.split()
        image_path = values[0]
        sentiment = int(values[1])

        # Load image
        im = caffe.io.load_image(image_path)

        # Make a forward pass
        out = net_full_conv.forward_all(data=np.asarray([transformer.preprocess('data', im)]))

        # Save the 2x8x8 prediction
        image_name = image_path.split('/')[-1]
        np.save(output_folder + image_name.split('.',2)[0], out['prob'][0])

    file.close()

