import argparse
import time
import datetime

import cv2
import gluoncv as gcv
import mxnet as mx
import numpy as np
import boto3

def parse_args():
    parser = argparse.ArgumentParser(description="Webcam object detection script",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--num-frames', type=int, default=200,
                        help='number of frames to run the demo for. -1 means infinite')

    parser.add_argument('--s3-bucket', type=str, default='adesojia-worker-safety')


    return parser.parse_args()

def main():
    args = parse_args()
    
    # Load the model
    net = gcv.model_zoo.get_model('ssd_512_mobilenet1.0_voc', pretrained=True)

    # Load the webcam handler
    cap = cv2.VideoCapture(0)
    time.sleep(1)  ### letting the camera autofocus

    NUM_FRAMES = args.num_frames
    i = 0
    while i < NUM_FRAMES or NUM_FRAMES == -1:
        i += 1

        # Load frame from the camera
        ret, frame = cap.read()

        # Image pre-processing
        cvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = mx.nd.array(cvframe).astype('uint8')
        rgb_nd, scaled_frame = gcv.data.transforms.presets.ssd.transform_test(frame, short=512, max_size=700)

        # Run frame through network
        class_IDs, scores, bounding_boxes = net(rgb_nd)

        if person_detected(class_IDs, scores, net.classes):
            rfr = cv2.resize(cvframe, (672, 380))
            push_to_s3(rfr, args.s3_bucket)

        # Display the result
        scale = 1.0 * frame.shape[0] / scaled_frame.shape[0]
        img = gcv.utils.viz.cv_plot_bbox(frame.asnumpy(), bounding_boxes[0], scores[0], class_IDs[0], class_names=net.classes, scale=scale)
        gcv.utils.viz.cv_plot_image(img)
        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()

def person_detected(class_IDs, scores, classes):
    high_confidence = class_IDs[0].asnumpy()[np.where(scores[0].asnumpy() > .5)]
    return classes.index('person') in high_confidence


def push_to_s3(img, bucket_name):
    try:
        index = 0

        timestamp = int(time.time())
        now = datetime.datetime.now()
        key = "persons/{}_{}/{}_{}/{}_{}.jpg".format(now.month, now.day,
                                                   now.hour, now.minute,
                                                   timestamp, index)

        s3 = boto3.client('s3')

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        _, jpg_data = cv2.imencode('.jpg', img, encode_param)
        response = s3.put_object(ACL='public-read',
                                 Body=jpg_data.tostring(),
                                 Bucket=bucket_name,
                                 Key=key)
    except Exception as e:
        msg = "Pushing to S3 failed: " + str(e)
        print(msg)

if __name__ == '__main__':
    main()