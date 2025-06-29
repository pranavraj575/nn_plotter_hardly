import os


def to_head(projectpath):
    pathlayers = os.path.join(projectpath, 'layers/').replace('\\', '/')
    return r"""
\documentclass[border=8pt, multi, tikz]{standalone} 
\usepackage{import}
\subimport{""" + pathlayers + r"""}{init}
\usetikzlibrary{positioning}
\usetikzlibrary{3d} %for including external image 
"""


def to_cor():
    return r"""
\def\ConvColor{rgb:yellow,5;red,2.5;white,5}
\def\ConvReluColor{rgb:yellow,5;red,5;white,5}
\def\PoolColor{rgb:red,1;black,0.3}
\def\UnpoolColor{rgb:blue,2;green,1;black,0.3}
\def\FcColor{rgb:blue,5;red,2.5;white,5}
\def\FcReluColor{rgb:blue,5;red,5;white,4}
\def\SoftmaxColor{rgb:magenta,5;black,7}   
\def\SumColor{rgb:blue,5;green,15}
"""


def to_begin():
    return r"""
\newcommand{\copymidarrow}{\tikz \draw[-Stealth,line width=0.8mm,draw={rgb:blue,4;red,1;green,1;black,3}] (-0.3,0) -- ++(0.3,0);}

\begin{document}
\begin{tikzpicture}
\tikzstyle{connection}=[ultra thick,every node/.style={sloped,allow upside down},draw=\edgecolor,opacity=0.7]
\tikzstyle{copyconnection}=[ultra thick,every node/.style={sloped,allow upside down},draw={rgb:blue,4;red,1;green,1;black,3},opacity=0.7]
"""


# layers definition

def to_input(pathfile, to='(-3,0,0)', width=8, height=8, name="temp", invert=False):
    return r"""
\node[canvas is zy plane at x=0] (""" + name + """) at """ + to + " {" + (
        r'\scalebox{-1}[1]{' if invert else '') + r"""\includegraphics[width=""" + str(
        width) + "cm" + """,height=""" + str(height) + "cm" + """]{""" + pathfile + ("}" if invert else "") + """}};
"""


# generic
def to_generic(name, obj='Box',
               offset="(0,0,0)", to="(0,0,0)",
               fill=r'\ConvColor',
               xlabel=None, ylabel=None, zlabel=None,
               width=None, height=None, depth=None,
               caption=None,
               invisible=False,
               **kwargs
               ):
    """
    :param invisible: removes bordering lines
        if you want a fully invisible box, make sure opacity=0 is in kwargs
    :param kwargs:
    :return:
    """
    bounded = ['xlabel', ]

    kwargs['name'] = name
    kwargs['caption'] = caption
    kwargs['fill'] = fill
    kwargs['height'] = height
    kwargs['width'] = width
    kwargs['depth'] = depth
    kwargs['xlabel'] = xlabel
    kwargs['ylabel'] = ylabel
    kwargs['zlabel'] = zlabel
    s = r"""
\pic[shift={""" + offset + "}," + ('draw=none,opacity=0,' if invisible else '') + "] at " + to + """
    {""" + obj + """={
        name=""" + name + """,
        caption=""" + caption + ",\n"
    for key in kwargs:
        if kwargs[key] is None:
            continue
        if key in bounded:
            kwargs[key] = "{{ " + str(kwargs[key]) + ", }}"
        s += ' '*8 + key + '=' + str(kwargs[key]) + ',\n'
    s += "        }\n    };\n"
    return s


# Conv
def to_Conv(name,
            zlabel=None, xlabel=None,
            offset="(0,0,0)", to="(0,0,0)",
            width=1, height=40,
            depth=40, caption=" ",
            fill=r'\ConvColor',
            invisible=False,
            **kwargs,
            ):
    return to_generic(name=name,
                      obj='Box',
                      fill=fill,
                      xlabel=xlabel,
                      zlabel=zlabel,
                      offset=offset,
                      to=to,
                      height=height,
                      width=width,
                      depth=depth,
                      caption=caption,
                      invisible=invisible,
                      **kwargs,
                      )


# Conv,Conv,relu
# Bottleneck
def to_ConvConvRelu(name,
                    zlabel=None, xlabel=None,
                    offset="(0,0,0)", to="(0,0,0)",
                    height=40, width=2, depth=40,
                    caption=" ",
                    **kwargs,
                    ):
    if type(width) != tuple:
        width = (width,)
    if xlabel is not None:
        if type(xlabel) != tuple:
            xlabel = (xlabel,)
        if type(xlabel) == tuple and type(width) != tuple:
            width = tuple(width for _ in xlabel)
        if type(width) == tuple and type(xlabel) != tuple:
            xlabel = tuple(xlabel for _ in width)

    return to_generic(name=name,
                      obj='RightBandedBox',
                      xlabel=None if xlabel is None else ", ".join(str(x) for x in xlabel),
                      zlabel=zlabel,
                      offset=offset,
                      to=to,
                      height=height,
                      width='{' + ", ".join(str(w) for w in width) + '}',
                      depth=depth,
                      caption=caption,
                      fill=r'\ConvColor',
                      bandfill=r'\ConvReluColor',
                      **kwargs,
                      )


# Pool
def to_Pool(name,
            offset="(0,0,0)", to="(0,0,0)",
            height=32, width=1, depth=32,
            opacity=0.5,
            caption=" ",
            fill=r'\PoolColor',
            **kwargs,
            ):
    return to_generic(name, obj='Box',
                      offset=offset, to=to,
                      width=width, height=height, depth=depth,
                      caption=caption,
                      opacity=opacity,
                      fill=fill,
                      **kwargs,
                      )


# unpool4,
def to_UnPool(name, offset="(0,0,0)", to="(0,0,0)", width=1, height=32, depth=32, opacity=0.5, caption=" "):
    return r"""
\pic[shift={ """ + offset + """ }] at """ + to + """ 
    {Box={
        name=""" + name + r""",
        caption=""" + caption + r""",
        fill=\UnpoolColor,
        opacity=""" + str(opacity) + """,
        height=""" + str(height) + """,
        width=""" + str(width) + """,
        depth=""" + str(depth) + """
        }
    };
"""


def to_ConvRes(name, s_filer=256, n_filer=64, offset="(0,0,0)", to="(0,0,0)", width=6, height=40, depth=40, opacity=0.2,
               caption=" "):
    return r"""
\pic[shift={ """ + offset + """ }] at """ + to + """ 
    {RightBandedBox={
        name=""" + name + """,
        caption=""" + caption + """,
        xlabel={{ """ + str(n_filer) + """, }},
        zlabel=""" + str(s_filer) + r""",
        fill={rgb:white,1;black,3},
        bandfill={rgb:white,1;black,2},
        opacity=""" + str(opacity) + """,
        height=""" + str(height) + """,
        width=""" + str(width) + """,
        depth=""" + str(depth) + """
        }
    };
"""


# ConvSoftMax
def to_ConvSoftMax(name, s_filer=40, offset="(0,0,0)", to="(0,0,0)", width=1, height=40, depth=40, caption=" "):
    return r"""
\pic[shift={""" + offset + """}] at """ + to + """ 
    {Box={
        name=""" + name + """,
        caption=""" + caption + """,
        zlabel=""" + str(s_filer) + r""",
        fill=\SoftmaxColor,
        height=""" + str(height) + """,
        width=""" + str(width) + """,
        depth=""" + str(depth) + """
        }
    };
"""


# SoftMax
def to_SoftMax(name,
               s_filer=10,
               offset="(0,0,0)", to="(0,0,0)",
               height=3, width=1.5, depth=25,
               opacity=0.8,
               caption=" ",
               **kwargs, ):
    return to_generic(name=name,
                      obj='Box',
                      offset=offset,
                      to=to,
                      fill=r'\SoftmaxColor',
                      xlabel='" ","dummy"',
                      zlabel=s_filer,
                      height=height,
                      width=width,
                      depth=depth,
                      caption=caption,
                      opacity=opacity,
                      **kwargs,
                      )


def to_Sum(name,
           offset="(0,0,0)", to="(0,0,0)",
           radius=2.5,
           opacity=0.6,
           **kwargs,
           ):
    return to_generic(name=name,
                      obj='Ball',
                      offset=offset,
                      to=to,
                      fill=r'\SumColor',
                      logo='$+$',
                      opacity=opacity,
                      radius=radius,
                      **kwargs,
                      )


def to_connection(of, to):
    return r"""
\draw [connection]  (""" + of + r""")    -- node {\midarrow} (""" + to + """);
"""


def to_dotted_diags(of, to):
    return r"""
\draw[densely dashed]
    (""" + of + """-nearnortheast) - - (""" + to + """-nearnorthwest)
    (""" + of + """-nearsoutheast) - - (""" + to + """-nearsouthwest)
    (""" + of + """-farsoutheast) - - (""" + to + """-farsouthwest)
    (""" + of + """-farnortheast) - - (""" + to + """-farnorthwest)
;"""


def to_skip(of, to, pos=1.25):
    return r"""
\path (""" + of + """-southeast) -- (""" + of + """-northeast) coordinate[pos=""" + str(pos) + """] (""" + of + """-top) ;
\path (""" + to + """-south)  -- (""" + to + """-north)  coordinate[pos=""" + str(pos) + """] (""" + to + """-top) ;
\draw [copyconnection]  (""" + of + """-northeast)  
-- node {\copymidarrow}(""" + of + """-top)
-- node {\copymidarrow}(""" + to + """-top)
-- node {\copymidarrow} (""" + to + """-north);
"""


def to_end():
    return r"""
\end{tikzpicture}
\end{document}
"""


def to_generate(arch, pathname="file.tex"):
    with open(pathname, "w") as f:
        for c in arch:
            print(c)
            f.write(c)


if __name__ == '__main__':
    print(to_Conv('test'))
    print(to_generic('test',
                     zlabel=256, xlabel=64,
                     offset="(0,0,0)", to="(0,0,0)",
                     width=1, height=40, depth=40, caption=" "))
    print()
    print(to_ConvConvRelu('test'))
