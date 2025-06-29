import sys

import numpy as np

sys.path.append('../')
from pycore.tikzeng import *


def len_map(dim, img=False):
    if img:
        factor = .21
    else:
        factor = 1
    return np.clip(factor*np.power(dim, .5)*1.5, .69, 36.9)


# defined your arch
shift = 3.9
p = .5
goal_vec_len = 4
initial_img_channels = 3
q = 1 - p
keys = ('front', 'bottom')
# keys=('front',)
arch = [
           to_head('..'),
           to_cor(),
           to_begin(), ] + sum([
    [
        to_Conv("invis" + typ,
                offset="(0," + str((1 if typ == 'front' else -1)*shift) + ",0)", to="(0,0,0)",
                width=.00069, height=len_map(240), depth=len_map(320),
                opacity=0,
                invisible=False,  # so that caption is visible
                caption="\\mbox{" + typ.capitalize() + " Optic Flow}",
                ),
        to_input(pathfile=os.path.join(os.path.dirname(__file__), 'optic_flow_' + typ + '_34.png'),
                 to='(invis' + typ + '-east)', name='opticflowf', height=len_map(240, img=True),
                 width=len_map(320, img=True)),

        to_Conv("conv1" + typ,
                offset="(2,0,0)", to='(invis' + typ + '-east)',
                width=len_map(initial_img_channels), height=len_map(240), depth=len_map(320),
                fill='{rgb:' + ('red' if typ == 'front' else 'blue') + ',1;black,0.3}',
                **(dict(xlabel=initial_img_channels, ylabel=240,
                        zlabel='~'*8 + str(320), ) if typ == 'front' else dict()),
                ),

        to_dotted_diags('invis' + typ, 'conv1' + typ),
        to_Pool("pool1" + typ,
                offset="(1.5,0,0)", to="(conv1" + typ + "-east)",
                height=len_map(60), depth=len_map(80), width=len_map(initial_img_channels),
                caption="MaxPool" if typ == 'front' else ' ',
                fill='{rgb:' + ('red' if typ == 'front' else 'blue') + ',1;black,0.3}',
                **(dict(xlabel=initial_img_channels, ylabel=60,
                        zlabel='~'*8 + str(80), ) if typ == 'front' else dict()),
                ),
        to_dotted_diags('conv1' + typ, 'pool1' + typ),
        to_ConvConvRelu("conv2" + typ,
                        offset="(1.25,0,0)", to="(pool1" + typ + "-east)",
                        width=len_map(16), height=len_map(19), depth=len_map(26),
                        caption="{CNN+ReLU}" if typ == 'front' else ' ',
                        **(dict(xlabel=16, ylabel=19, zlabel='~'*4 + str(26), ) if typ == 'front' else dict()),
                        ),
        to_connection("pool1" + typ + '-east', "conv2" + typ + '-west'),

        to_Pool("pool2" + typ,
                offset="(0.5,0,0)", to="(conv2" + typ + "-east)",
                width=len_map(16), height=len_map(9), depth=len_map(13),
                caption="MaxPool" if typ == 'front' else ' ',
                **(dict(xlabel=16, ylabel=9, zlabel='~'*4 + str(13), ) if typ == 'front' else dict()),
                fill='{rgb:' + ('red' if typ == 'front' else 'blue') + ',1;black,0.3}',
                ),
        to_dotted_diags('conv2' + typ, 'pool2' + typ),

        to_Conv("flatten" + typ,
                offset="(2," + str((-q if typ == 'front' else p)*shift) + ",0)",
                to="(pool2" + typ + "-east)",
                width=len_map(0), height=len_map(0), depth=len_map(1872),
                caption="Flatten" if typ == 'front' else ' ',
                fill='{rgb:' + ('red' if typ == 'front' else 'blue') + ',1;black,0.3}',
                **(dict(zlabel='~'*32 + str(1872), ) if typ == 'front' else dict()),
                ),
        to_dotted_diags('pool2' + typ, 'flatten' + typ),

        to_Conv("concat" + typ, zlabel='~'*8 + str(1872*2 + goal_vec_len) if typ == 'bottom' else ' ',
                offset="(2.5," +
                       str((-q if typ == 'front' else p)*shift) + "," +
                       str(.1*(-1 if typ == 'front' else 1)*len_map(1872)) + ")",
                to="(flatten" + typ + "-east)",
                width=len_map(0), height=len_map(0), depth=len_map(1872),
                caption="Concatenate" if typ == 'bottom' else ' ',
                fill='{rgb:' + ('red' if typ == 'front' else 'blue') + ',1;black,0.3}',
                **(dict() if typ == 'front' else dict()),
                ),
        to_dotted_diags('flatten' + typ, 'concat' + typ),
    ] for typ in keys], []
) + [
           to_Conv("goal",
                   offset="(0," + str(.69*shift) + ",0)", to='(conv1front-north)',
                   width=len_map(0), height=len_map(0), depth=len_map(goal_vec_len),
                   fill='{rgb:green,1;black,0.3}',
                   zlabel=str(goal_vec_len),
                   caption='\\mbox{Goal Vector}'
                   ),
           to_Conv("goal2",
                   offset="(0,0," + str(-(.15/2)*goal_vec_len) + ")", to='(concatfront-farwest)',
                   width=len_map(0), height=len_map(0), depth=len_map(goal_vec_len),
                   fill='{rgb:green,1;black,0.3}',
                   ),
           to_dotted_diags('goal', 'goal2'),
       ] + [
           to_ConvConvRelu("linear", zlabel='~'*8 + str(64),
                           offset="(1,0,0)", to="(concat" + 'front' + "-neareast)",
                           width=tuple([len_map(0) for _ in range(1)]), height=len_map(0), depth=len_map(64),
                           caption="{Linear+Tanh}",
                           ),
           to_connection("concat" + 'front' + '-neareast', "linear" + '-west'),

           to_Conv("output", zlabel=2,
                   offset="(1.5,0,0)", to="(linear-east)",
                   width=len_map(0), height=len_map(0), depth=len_map(2),
                   caption='Output',
                   # caption="\\hspace{-20 pt}\mbox{Output}",
                   ),
           to_connection("linear" + '-east', "output" + '-west'),

           to_Conv("invis2",
                   offset="(.25,0,0)", to="(output-east)",
                   width=1, height=1, depth=1,
                   opacity=0,
                   invisible=True,
                   ),
           to_end()
       ]


def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex')


if __name__ == '__main__':
    main()
