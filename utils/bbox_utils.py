def get_center(bbox):
    x1, y1, x2, y2 = bbox
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))

def measure_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def get_foot_position(bbox):
    x1, y1, x2, y2 = bbox
    return (int((x1 + x2) / 2), y2)

def get_closest_keypoint(point, keypoints, keypoint_indices):
    min_distance = float('inf')
    closest_keypoint = keypoint_indices[0]
    
    for keypoint_index in keypoint_indices:
        keypoint = keypoints[keypoint_index * 2], keypoints[keypoint_index * 2 + 1]
        distance = abs(point[1] - keypoint[1])
        
        if distance < min_distance:
            min_distance = distance
            closest_keypoint = keypoint_index
            
    return closest_keypoint

def get_height_of_bbox(bbox):
    return bbox[3] - bbox[1]

def measure_xy_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2), abs(y1 - y2)

def get_center_of_bbox(bbox):
    x1, y1, x2, y2 = bbox
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))