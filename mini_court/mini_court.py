import cv2
import sys
import numpy as np

sys.path.append("../")
import constants
from utils import (
    convert_pixel_distance_to_metres,
    convert_metres_to_pixel_distance,
    get_foot_position,
    get_closest_keypoint,
    get_height_of_bbox,
    measure_xy_distance,
    get_center_of_bbox,
    measure_distance
)

class MiniCourt():
    def __init__(self, frame):
        self.drawing_rectangle_width = 250
        self.drawing_rectangle_height = 500
        self.buffer = 50
        self.padding_court = 20
        
        self.set_canvas_background_box_position(frame)
        self.set_mini_court_position()
        self.set_court_drawing_keypoints()
        self.set_court_lines()
        
    def convert_metres_to_pixels(self, metres):
        return convert_metres_to_pixel_distance(
            metres,
            constants.DOUBLE_LINE_WIDTH,
            self.court_drawing_width
        )
        
    def set_court_drawing_keypoints(self):
        drawing_key_points = [0]*28

        # point 0 
        drawing_key_points[0] , drawing_key_points[1] = int(self.court_start_x), int(self.court_start_y)
        # point 1
        drawing_key_points[2] , drawing_key_points[3] = int(self.court_end_x), int(self.court_start_y)
        # point 2
        drawing_key_points[4] = int(self.court_start_x)
        drawing_key_points[5] = self.court_start_y + self.convert_metres_to_pixels(constants.HALF_COURT_LINE_HEIGHT*2)
        # point 3
        drawing_key_points[6] = drawing_key_points[0] + self.court_drawing_width
        drawing_key_points[7] = drawing_key_points[5] 
        # #point 4
        drawing_key_points[8] = drawing_key_points[0] + self.convert_metres_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
        drawing_key_points[9] = drawing_key_points[1] 
        # #point 5
        drawing_key_points[10] = drawing_key_points[4] + self.convert_metres_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
        drawing_key_points[11] = drawing_key_points[5] 
        # #point 6
        drawing_key_points[12] = drawing_key_points[2] - self.convert_metres_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
        drawing_key_points[13] = drawing_key_points[3] 
        # #point 7
        drawing_key_points[14] = drawing_key_points[6] - self.convert_metres_to_pixels(constants.DOUBLE_ALLY_DIFFERENCE)
        drawing_key_points[15] = drawing_key_points[7] 
        # #point 8
        drawing_key_points[16] = drawing_key_points[8] 
        drawing_key_points[17] = drawing_key_points[9] + self.convert_metres_to_pixels(constants.NO_MANS_LAND_HEIGHT)
        # # #point 9
        drawing_key_points[18] = drawing_key_points[16] + self.convert_metres_to_pixels(constants.SINGLE_LINE_WIDTH)
        drawing_key_points[19] = drawing_key_points[17] 
        # #point 10
        drawing_key_points[20] = drawing_key_points[10] 
        drawing_key_points[21] = drawing_key_points[11] - self.convert_metres_to_pixels(constants.NO_MANS_LAND_HEIGHT)
        # # #point 11
        drawing_key_points[22] = drawing_key_points[20] +  self.convert_metres_to_pixels(constants.SINGLE_LINE_WIDTH)
        drawing_key_points[23] = drawing_key_points[21] 
        # # #point 12
        drawing_key_points[24] = int((drawing_key_points[16] + drawing_key_points[18])/2)
        drawing_key_points[25] = drawing_key_points[17] 
        # # #point 13
        drawing_key_points[26] = int((drawing_key_points[20] + drawing_key_points[22])/2)
        drawing_key_points[27] = drawing_key_points[21] 

        self.drawing_key_points = drawing_key_points
        
    def set_court_lines(self):#
        self.lines = [
            (0, 2),
            (4, 5),
            (6,7),
            (1,3),
            (0,1),
            (8,9),
            (10,11),
            (10,11),
            (2,3)
        ]
        
    def set_mini_court_position(self):
        self.court_start_x = self.start_x + self.padding_court
        self.court_start_y = self.start_y + self.padding_court
        
        self.court_end_x = self.end_x - self.padding_court
        self.court_end_y = self.end_y - self.padding_court
        
        self.court_drawing_width = self.court_end_x - self.court_start_x
        
    def set_canvas_background_box_position(self, frame):
        frame = frame.copy()
        
        self.end_x = frame.shape[1] - self.buffer
        self.end_y = self.buffer + self.drawing_rectangle_height
        
        self.start_x = self.end_x - self.drawing_rectangle_width
        self.start_y = self.end_y - self.drawing_rectangle_height
        
    def draw_court(self, frame):
        # draw the keypoints
        for i in range(0, len(self.drawing_key_points), 2):
            x = int(self.drawing_key_points[i])
            y = int(self.drawing_key_points[i+1])
            cv2.circle(frame, (x, y), 5, (255, 0, 0), cv2.FILLED)
            
        # draw the lines
        for line in self.lines:
            start_point = (int(self.drawing_key_points[line[0] * 2]), int(self.drawing_key_points[line[0] * 2 + 1]))
            end_point = (int(self.drawing_key_points[line[1] * 2]), int(self.drawing_key_points[line[1] * 2 + 1]))
            cv2.line(frame, start_point, end_point, (0, 0, 0), 2)
            
        # draw the net
        net_start_point = (self.drawing_key_points[0], int((self.drawing_key_points[1] + self.drawing_key_points[5]) / 2))
        net_end_point = (self.drawing_key_points[2], int((self.drawing_key_points[1] + self.drawing_key_points[5]) / 2))
        cv2.line(frame, net_start_point, net_end_point, (255, 0, 0), 2)
            
        return frame
        
    def draw_background_rectangle(self, frame):
        shapes = np.zeros_like(frame, np.uint8)
        
        # Draw rectangle
        cv2.rectangle(shapes, (self.start_x, self.start_y), (self.end_x, self.end_y), (255, 255, 255), cv2.FILLED)
        
        out = frame.copy()
        alpha = 0.5
        
        mask = shapes.astype(bool)
        out[mask] = cv2.addWeighted(frame, alpha, shapes, 1 - alpha, 0)[mask]
        
        return out
    
    def draw_mini_court(self, frames):
        output_frames = []
        
        for frame in frames:
            frame = self.draw_background_rectangle(frame)
            frame = self.draw_court(frame)
            
            output_frames.append(frame)
            
        return output_frames
    
    def get_mini_court_coords(self, 
                              object_position, 
                              closest_keypoint, 
                              closest_keypoint_index, 
                              player_height_in_pixels,
                              player_height_in_metres):
        distance_from_keypoint_x_pixels, distance_from_keypoint_y_pixels = measure_xy_distance(object_position, closest_keypoint)
        
        # convert pixel distance to metres
        distances_from_keypoint_x_metres = convert_pixel_distance_to_metres(distance_from_keypoint_x_pixels,
                                                                            player_height_in_metres,
                                                                            player_height_in_pixels)
        distances_from_keypoint_y_metres = convert_pixel_distance_to_metres(distance_from_keypoint_y_pixels,
                                                                            player_height_in_metres,
                                                                            player_height_in_pixels)
        
        # convert to minicourt coordinates
        mini_court_x_distance_pixels = self.convert_metres_to_pixels(distances_from_keypoint_x_metres)
        mini_court_y_distance_pixels = self.convert_metres_to_pixels(distances_from_keypoint_y_metres)
        
        closest_mini_court_keypoint = (self.drawing_key_points[closest_keypoint_index * 2], 
                                       self.drawing_key_points[closest_keypoint_index * 2 + 1])
        
        mini_court_player_position = (closest_mini_court_keypoint[0] + mini_court_x_distance_pixels,
                                      closest_mini_court_keypoint[1] + mini_court_y_distance_pixels)
        
        return mini_court_player_position
    
    def convert_bbox_to_mini_court(self, player_boxes, ball_boxes, original_court_keypoints):
        player_heights = {
            1: constants.PLAYER_1_HEIGHT,
            2: constants.PLAYER_2_HEIGHT,
        }
        
        output_player_boxes = []
        output_ball_boxes = []
        
        for frame_num, player_bbox in enumerate(player_boxes):
            ball_box = ball_boxes[frame_num][1]
            ball_position = get_center_of_bbox(ball_box)
            
            closest_player_id_to_ball = min(player_bbox.keys(), key=lambda x: measure_distance(ball_position, get_center_of_bbox(player_bbox[x])))
            
            output_player_bboxes_dict = {}
            output_ball_bboxes = []
            for player_id, bbox in player_bbox.items():
                foot_position = get_foot_position(bbox)
                # get closest keypoint
                closest_keypoint_index = get_closest_keypoint(foot_position, original_court_keypoints, [0, 2, 12, 13])
                closest_keypoint = (original_court_keypoints[closest_keypoint_index * 2], 
                                    original_court_keypoints[closest_keypoint_index * 2 + 1])
                # get player height in pixels
                frame_index_min = max(0, frame_num - 20)
                frame_index_max = min(len(player_boxes), frame_num + 20)
                
                bboxes_height_in_pixels = [get_height_of_bbox(player_boxes[i][player_id]) for i in range(frame_index_min, frame_index_max)]
                max_player_height_in_pixels = max(bboxes_height_in_pixels)
                
                mini_court_player_position = self.get_mini_court_coords(foot_position, 
                                                                        closest_keypoint, 
                                                                        closest_keypoint_index, 
                                                                        max_player_height_in_pixels, 
                                                                        player_heights[player_id])
                
                output_player_bboxes_dict[player_id] = mini_court_player_position
                
                if closest_player_id_to_ball == player_id:
                    closest_keypoint_index = get_closest_keypoint(ball_position, original_court_keypoints, [0, 2, 12, 13])
                    closest_keypoint = (original_court_keypoints[closest_keypoint_index * 2], original_court_keypoints[closest_keypoint_index * 2 + 1])
                
                    mini_court_ball_position = self.get_mini_court_coords(ball_position, 
                                                                            closest_keypoint, 
                                                                            closest_keypoint_index, 
                                                                            max_player_height_in_pixels, 
                                                                            player_heights[player_id])
                    
                    output_ball_bboxes.append({1: mini_court_ball_position})
            output_player_boxes.append(output_player_bboxes_dict)
            
        return output_player_boxes, output_ball_bboxes
    
    def draw_points_on_mini_court(self, frames, positions, color=(0, 255, 0)):
        for frame_num, frame in enumerate(frames):
            for _, position in positions[frame_num].items():
                x, y = position
                x = int(x)
                y = int(y)
                cv2.circle(frame, (x, y), 5, color, cv2.FILLED)
                
        return frames
                    
    def get_start_point_of_mini_court(self):
        return (self.court_start_x, self.court_start_y)
    
    def get_width_of_mini_court(self):
        return self.court_drawing_width
    
    def get_court_drawing_keypoints(self):
        return self.drawing_key_points