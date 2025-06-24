import sys

import numpy as np

sys.path.append('../')
from pycore.tikzeng import *


def len_map(dim, img=False):
    if img:
        factor = .21
    else:
        factor = 1
    return np.clip(factor*np.power(dim, .5)*1.5, 1, 69)


# defined your arch
arch = [
    to_head('..'),
    to_cor(),
    to_begin(),
    to_Conv("invis",
            offset="(-2,0,0)", to="(0,0,0)",
            width=.1, height=len_map(240), depth=len_map(320),
            # caption="Input Optic Flow",
            fill='{rgb:red,1;black,0.3}'
            ),
    to_input(pathfile=os.path.join(os.path.dirname(__file__), 'optic_flow_107.png'),
             to='(invis-east)', name='opticflow', height=len_map(240, img=True), width=len_map(320, img=True)),
    to_Conv("conv1", xlabel=3, ylabel=240, zlabel='~'*8 + str(320),
            offset="(0,0,0)", to="(0,0,0)",
            width=len_map(3), height=len_map(240), depth=len_map(320),
            caption="Input Optic Flow",
            fill='{rgb:red,1;black,0.3}'
            ),

    to_dotted_diags('invis', 'conv1'),
    to_Pool("pool1", xlabel=3, ylabel=60, zlabel='~'*8 + str(80),
            offset="(1,0,0)", to="(conv1-east)",
            height=len_map(60), depth=len_map(80), width=len_map(3),
            caption="MaxPool",
            ),
    to_dotted_diags('conv1', 'pool1'),
    to_ConvConvRelu("conv2", xlabel=16, ylabel=19, zlabel='~'*4 + str(26),
                    offset="(2,0,0)", to="(pool1-east)",
                    width=len_map(16), height=len_map(19), depth=len_map(26),
                    caption="{CNN+ReLU}",
                    ),
    to_connection("pool1", "conv2"),

    to_Pool("pool2", xlabel=16, ylabel=9, zlabel='~'*4 + str(13),
            offset="(0.5,0,0)", to="(conv2-east)",
            width=len_map(16), height=len_map(9), depth=len_map(13),
            caption="MaxPool",
            ),
    to_dotted_diags('conv2', 'pool2'),

    to_Conv("flatten", zlabel='~'*8 + str(1872),
            offset="(2,0,0)", to="(pool2-east)",
            width=len_map(0), height=len_map(0), depth=len_map(1872),
            caption="Flatten",
            fill='{rgb:red,1;black,0.3}',
            ),
    # to_connection("pool2", "flatten"),
    to_dotted_diags('pool2', 'flatten'),

    to_ConvConvRelu("linear", zlabel='~'*8 + str(64),
                    offset="(1,0,0)", to="(flatten-east)",
                    width=len_map(0), height=len_map(0), depth=len_map(64),
                    caption="{Linear+Tanh}",
                    ),
    to_connection("flatten", "linear"),

    to_Conv("output", zlabel=2,
            offset="(2,0,0)", to="(linear-east)",
            width=len_map(0), height=len_map(0), depth=len_map(2),
            # caption="\\hspace{-20 pt}\mbox{Output}",
            ),
    to_connection("linear", "output"),

    # to_ConvConvRelu("conv3", to='(pool2-east)', n_filer=64, width=2),
    # to_SoftMax("soft1", 10, "(3,0,0)", "(conv3-east)", caption="SOFT"),
    to_end()
]


def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex')


if __name__ == '__main__':
    main()
