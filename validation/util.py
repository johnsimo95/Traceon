import time
import argparse

from pygmsh import *
import matplotlib.pyplot as plt

import traceon.geometry as G
import traceon.excitation as E
import traceon.solver as S
import traceon.plotting as P

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-MSF', default=None, type=int, help='Mesh size factor')
parser.add_argument('--symmetry', choices=['3d', 'radial'], default='radial', help='Choose the symmetry to use for the geometry (3d or radially symmetric)')
parser.add_argument('--plot-accuracy', action='store_true', help='Plot the accuracy as a function of time and number of elements')
parser.add_argument('--plot-geometry', action='store_true', help='Plot the geometry')

def print_info(Nlines, duration, accuracy):
    print('Number of elements\t\tComputation time (ms)\t\tAccuracy')
    
    for N, d, a in zip(Nlines, duration, accuracy):
        print('%d\t\t\t\t%.1f\t\t\t\t%.1e' % (N, d, a))

default_msf_radial = [10, 25, 50, 100, 150]
default_msf_3d = [20, 50, 100, 200]

def parse_validation_args(create_geometry, compute_error, MSF={'radial':default_msf_radial, '3d':default_msf_3d}, **colors):
     
    args = parser.parse_args()
    MSFdefault = args.MSF if args.MSF != None else MSF[args.symmetry][1]
    symmetry = G.Symmetry.RADIAL if args.symmetry == 'radial' else G.Symmetry.THREE_D
    
    if args.plot_geometry:
        geom = create_geometry(MSFdefault, symmetry, True)
        assert geom.symmetry == symmetry 
        if geom.symmetry != G.Symmetry.THREE_D:
            P.plot_line_mesh(geom.mesh, **colors) 
        else:
            P.plot_triangle_mesh(geom.mesh, **colors)
    elif args.plot_accuracy:
        num_lines = []
        times = []
        errors = []

        for n in MSF[args.symmetry]:
            print('-'*75, f' MSF={n}')
            st = time.time()
            geom = create_geometry(n, symmetry, False)
            N, err = compute_error(geom)
            num_lines.append(N)
            times.append( (time.time() - st)*1000)
            errors.append(abs(err))
        
        print_info(num_lines, times, errors)

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        plt.sca(ax1)
        plt.xlabel('Number of elements')
        plt.ylabel('Accuracy (relative error)')
        plt.yscale('log')
        plt.xscale('log')
        plt.plot(num_lines, errors)
        plt.scatter(num_lines, errors)

        plt.sca(ax2)
        plt.plot(times, errors)
        plt.scatter(times, errors)
        plt.xlabel('Computation time (ms)')
        plt.ylabel('Accuracy (relative error)')
        plt.yscale('log')
        
        plt.sca(ax3)
        plt.plot(num_lines, times)
        plt.scatter(num_lines, times)
        plt.xlabel('Number of elements')
        plt.ylabel('Computation time (ms)')
        plt.show()

    else:
        st = time.time()
        geom = create_geometry(MSFdefault, symmetry, False)
        N, err = compute_error(geom)
        duration = (time.time() - st)*1000
        print_info([N], [duration], [err])



