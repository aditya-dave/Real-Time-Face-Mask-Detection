import tensorflow as tf
from object_detection.utils import config_util
from object_detection.protos import pipeline_pb2
from google.protobuf import text_format

CONFIG_PATH = 'FaceMaskNew/Tensorflow/workspace/models/my_ssd_mobnet/pipeline.config'
config = config_util.get_configs_from_pipeline_file(CONFIG_PATH)

import os
# %tensorflow_version 1.x
import tensorflow as tf
# from tensorflow.python.compiler.tensorrt import trt_convert as trt
from object_detection.protos import model_pb2
# from tensorflow.contrib import slim
from nets import inception_resnet_v2
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder

# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(CONFIG_PATH)
detection_model = model_builder.build(model_config=configs['model'], is_training=False)
# detection_model = model_builder.build(model_config='/content/drive/MyDrive/Applied ML/FaceMaskNew/Tensorflow/workspace/models/my_ssd_mobnet/pipeline.config', is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join('FaceMaskNew/Tensorflow/workspace/models/my_ssd_mobnet', 'ckpt-6')).expect_partial()

@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections


import cv2
import numpy as np
# from google.colab.patches import cv2_imshow

category_index = label_map_util.create_category_index_from_labelmap('FaceMaskNew/Tensorflow/workspace/annotations/labelmap.pbtxt')
print(category_index)

# Setup capture
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    image_np = np.array(frame)

    # cv2.imshow('frame',frame)
    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)
    print(detections)
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    # detection_classes should be ints.
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    label_id_offset = 1
    image_np_with_detections = image_np.copy()

    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'],
        detections['detection_classes'] + label_id_offset,
        detections['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=5,
        min_score_thresh=.5,
        agnostic_mode=False)
    print("Trying to start cv2.imshow")
    cv2.imshow('object detection', cv2.resize(image_np_with_detections, (800, 600)))
    print("Started cv2.imshow")
    # cv2.waitKey(500)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        break