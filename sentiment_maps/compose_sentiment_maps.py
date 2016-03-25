import os
import sys
import argparse
import cv2
import numpy as np


parser = argparse.ArgumentParser(description='Compose sentiment maps generated with generate_sentiment_maps.py over images in the Twitter five-agrees dataset')
parser.add_argument('-p', '--predictions_path', help='folder where the sentiment maps generated with generate_sentiment_maps.py are stored')
parser.add_argument('-i', '--images_path', help='folder containing the original inputs')
parser.add_argument('-o', '--output_path', help='folder where the generated outputs will be stored')

args = parser.parse_args()

prediction_path = args.predictions_path
images_path = args.images_path
output_path = args.output_path

counter = 0
for path, dirs, files in os.walk(prediction_path):
    for fileName in files:
        # Get path to the image
        image_name = fileName.split('.',2)[0] + '.jpg'
        image_path = os.path.join(images_path,image_name)

        # Load prediction
        prediction = np.load(os.path.join(path,fileName))
        heatmap = np.zeros((prediction.shape[1], prediction.shape[2], 3)) # BGR
        heatmap[:,:,1] = 255*prediction[1] # positive (1) in green
        heatmap[:,:,2] = 255*prediction[0] # negative (0) in red

        # Load image
        img = cv2.imread(image_path)
        if img is None:
		  pass

        # Resize heatmap so it fits the image
        heatmap = cv2.resize(heatmap, tuple(img.shape[1::-1]), interpolation=cv2.INTER_NEAREST)

        # Combine image and heatmap
        output = 0.5*img + 0.5*heatmap

        # Save result
        cv2.imwrite(os.path.join(output_path,image_name), output)

        # Print progress
        counter += 1
        if counter%20 == 0:
            print 'Processed images: ' + str(counter)
            sys.stdout.flush()
