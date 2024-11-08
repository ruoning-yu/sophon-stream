//===----------------------------------------------------------------------===//
//
// Copyright (C) 2022 Sophgo Technologies Inc.  All rights reserved.
//
// SOPHON-STREAM is licensed under the 2-Clause BSD License except for the
// third-party components.
//
//===----------------------------------------------------------------------===//

#ifndef SOPHON_STREAM_ELEMENT_YOLOV8_CONTEXT_H_
#define SOPHON_STREAM_ELEMENT_YOLOV8_CONTEXT_H_

#include "algorithmApi/context.h"

namespace sophon_stream {
namespace element {
namespace yolov8 {

#define USE_ASPECT_RATIO 1

enum class TaskType { Detect = 0, Pose, Cls, Seg, Obb };

class Yolov8Context : public ::sophon_stream::element::Context {
 public:
  int deviceId;  // 设备ID

  std::shared_ptr<BMNNContext> bmContext;
  std::shared_ptr<BMNNNetwork> bmNetwork;
  bm_handle_t handle;

  std::vector<float> mean;  // 前处理均值， 长度为3，顺序为rgb
  std::vector<float> stdd;  // 前处理方差， 长度为3，顺序为rgb
  bool bgr2rgb;             // 是否将bgr图像转成rgb推理

  TaskType taskType = TaskType::Detect;

  float thresh_conf_min = -1;
  std::unordered_map<std::string, float> thresh_conf;  // 置信度阈值
  float thresh_nms;                                    // nms iou阈值
  std::vector<std::string> class_names;
  bool class_thresh_valid = false;

  int class_num = 80;  // default is coco names
  int m_frame_h, m_frame_w;
  int net_h, net_w, m_net_channel;
  int max_batch;
  int input_num;
  int output_num;  //
  int min_dim;
  bmcv_convert_to_attr converto_attr;

  bool use_post_opt = false;

  bmcv_rect_t roi;
  bool roi_predefined = false;
  int thread_number;

  // yolov8_seg_tpu_opt
  bool seg_tpu_opt = false;
  std::string mask_bmodel_path = "";
  bm_handle_t tpu_mask_handle;
  void *bmrt = nullptr;
  const bm_net_info_t *netinfo;
  std::vector<std::string> network_names;
  int mask_len = 32;
  int tpu_mask_num = 32;
  int m_tpumask_net_h, m_tpumask_net_w;

};
}  // namespace yolov8
}  // namespace element
}  // namespace sophon_stream

#endif  // SOPHON_STREAM_ELEMENT_YOLOV8_CONTEXT_H_