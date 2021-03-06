import sys
import getopt
import os
import struct
import datetime
import json
import operator
import csv
import numpy as np
import matplotlib.pyplot as plt

from copy import deepcopy
from pprint import pprint
from collections import Counter


def main():
    object_list = []
    encoding_vector = {}
    weight_vector = {}
    with open('../config/object_weight.csv', newline='') as csvfile:
        reader1 = csv.DictReader(csvfile)
        encoding_vector = objectEncodingVector(reader1)
            # encoding_vector[row['label']] = row['Number']
            # weight_vector[row['label']] = row['Weight']
            # print(row['label'], row['number'])

    with open('../config/object_weight.csv', newline='') as csvfile:
        reader2 = csv.DictReader(csvfile)
        for row in reader2:
            print(row['label'])
            object_list.append(row['label'])

    with open('../config/object_weight.csv', newline='') as csvfile:
        reader3 = csv.DictReader(csvfile)
        weight_vector = objectWeightVector(reader3)

    jsonString = "../data/faith.json"
    curr = []
    for line in open(jsonString, 'r'):
        curr.append(json.loads(line))
#    entry = {"oid": curr["timestamp"], "name": curr["frameName"], "objects": [], "labels": []}

    curr_list = []
    prev = []
    for ann in curr:
        temp = []
        frameName = ann['frameName']
        # print(frameName)
        for k in ann["annotations"]:
          # temp.append({"label": ''.join([i for i in k["label"] if not i.isdigit()]), "prob": k["prob"]})
            temp.append({"label": ''.join([i for i in k["label"] if not i.isdigit()]), "ytop": k["ytop"],
                        "ybottom": k["ybottom"], "xleft": k["xleft"], "xright": k["xright"], "prob": k["prob"], "frameName": frameName})

            '''
            1) check for porportion of common items, based on ann with fewer objects
            
            2) check for the probability of all common items, calculate the deviation based on squared root distance 

            #label using the name of the [three] most common items through all the annotation with highest prob 

            #give a maximum amount of timestamp interval between two segment?

            #once a new segment is created, update the previous/history information

            #create a default segement label called transition to handle unresolved cases


            '''
        curr_list.append(temp)

    # print(curr_list)

    figure_3 = np.zeros((100, len(curr_list)))
    print(figure_3.shape)

    frame_list = []
    # inital frame
    # print(curr_list[0])
    cnt = 0
    initial_frame = curr_list[0]
    last_frame = initial_frame
    frame_table = Counter()
    for item in initial_frame:
        frame_table[item['label']] += 1
        figure_3[int(encoding_vector[item['label']])][cnt] += 1

    # print(frame_table)

    for k in curr_list[1:]:
        cnt += 1
        ann_table = Counter()
        for item in k:
            ann_table[item['label']] += 1
            # print(encoding_vector[item['label']])
            figure_3[int(encoding_vector[item['label']])][cnt] += 1
        # print(ann_table)
        # print(figure_3[:,cnt])


        if not segmentDetection(frame_table, ann_table):
            figure_3[80:, cnt] = 20
            frame_list.append(labeling(initial_frame, last_frame, frame_table))
            initial_frame = k
            last_frame = initial_frame
            frame_table = ann_table
        else:
            last_frame = k

    # print(frame_list)
    with open('../data/yolo.json', 'w') as outfile:
        json.dump(frame_list, outfile)

    y = list(range(0, 80))

    # print(cnt)
    # print(figure_3[:,0])

    a = set()
    # for tmp_list in range(0,80):
    tmp = np.where(figure_3[:,:] >= 1)
    print(tmp[0])
    for i in tmp[0]:
        if i <80:
            a.add(i-1)
    print(a)

    object_list_2 = ["-"] * 80
    print(object_list)
    for i in a:
        print(i)
        object_list_2[i] = object_list[i]

    print(object_list_2)


    plt.imshow(figure_3)
    plt.xlim((0,600))
    plt.yticks(y, object_list_2,fontsize = 2.5)
    plt.colorbar(shrink=0.5)
    plt.xlabel('frame')
    plt.ylabel('object type')
    plt.title('scene segment')
    plt.show()

    return frame_list

def objectEncodingVector(weight_file):
    encoding_vector = {}

    for row in weight_file:
        encoding_vector[row['label']] = row['Number']
    return encoding_vector


def objectWeightVector(weight_file):
    weight_vector = {}

    for row in weight_file:
        weight_vector[row['label']] = row['Weight']
    return weight_vector


def objectVariationVector():
    pass


def distanceCalculation():
    pass


def labeling(first, last, table):
    object_list = ''
    for k,v in table.items():
        object_list += '_' + str(k) + '_' + str(v)
    print(first[-1]["frameName"] + '_' + last[-1]["frameName"] + object_list)
    return first[-1]["frameName"] + '_' + last[-1]["frameName"]

def segmentDetection(f_table, a_table):
    common_count = 0
    common_item = 0
    total_count = 0
    total_item = 0
    # print(a_table)
    for it, n in a_table.items():
        common_count += min(n,f_table[it])
        if common_count > 0:
            common_item += 1
        total_item += 1
        total_count += n

    if common_count/total_count > 0.8:
        return True
    elif common_count/total_count + common_item/total_item > 1:
        return True
    else:
        return False


    # objs = deepcopy([k for k in temp if item["label"] in k.itervalues()])
    # print(objs)



if __name__ == '__main__':
    main()
