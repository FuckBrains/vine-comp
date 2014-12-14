# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 14:36:33 2014

@author: sunshine
"""

import pandas as pd
from scraper import abs_path as ap
from scraper import vine_exists as exists
from moviepy import editor as mpe


def group_data(data, group_size):
    return [data[x:x+group_size] for x in range(0, len(data), group_size)]


def vfc_from_file(filename, directory):
    return mpe.VideoFileClip(ap(str(directory) + '/' + str(filename) + '.mp4'))


def write_x264(vfc, path):
    vfc.write_videofile(path, codec='libx264', threads=2, verbose=True, fps=30)


def render_vines(data):
    #converts specified index to ascii so it can be rendered
    encode_index = lambda data, index: (data.astype(basestring)[index]
                                            .encode('ascii', 'ignore'))
    #verify files exist in cache folder
    datav = exists(data, 'cache')
    datavrid = exists(data, 'render')['id'].astype(basestring)
    for i, vineid in enumerate(datav['id'].astype(basestring)):
        if vineid not in datavrid:
            vine = vfc_from_file(vineid, 'cache').on_color(size=(854, 480),
                                                           color=(20, 20, 25),
                                                           pos='center')
            #encodes text as ascii for textclip creation
            user = encode_index(data['username'], i)
            desc = encode_index(data['description'], i)
            user = 'Vine By:' + user
            #lambda to create text clip
            tc = lambda text, size: (mpe.TextClip(txt=text, size=(187, 480),
                                            method='caption', align='center',
                                            font='arial', fontsize=size,
                                            color='white', interline=20)
                                    .set_duration(vine.duration))
            user_osd = tc(user, 40)
            desc_osd = tc(desc, 28).set_pos('right')
                        
            #composite the text on the sides of the video
            comp = mpe.CompositeVideoClip([vine, user_osd, desc_osd])
            #start the render
            write_x264(comp, ap('render/' + vineid + '.mp4'))
        else:
            print('skipping ' + vineid)


def concat_vines(data):
    datavid = exists(data, 'render')['id']
    groups = group_data(datavid, 10)
    #lambda to get video from group number
    vfcg = lambda group: vfc_from_file('group_' + str(group), 'render/groups')
    group_render_path = lambda f: ap('render/groups/' + f + '.mp4')
    for i, group in enumerate(groups):
        videos = [vfc_from_file(vineid, 'render') for vineid in group]
        concat = mpe.concatenate_videoclips(videos)
        write_x264(concat, group_render_path('group_' + str(i)))
    videos = [vfcg(groupid) for groupid in range(len(groups))]
    concat = mpe.concatenate_videoclips(videos)
    write_x264(concat, group_render_path("FINAL RENDER"))


if __name__ == '__main__':
    data = pd.read_csv(ap('records.csv'), encoding='utf-8')
    render_vines(data)
    concat_vines(data)
