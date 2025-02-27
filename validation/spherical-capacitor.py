from math import cos

import matplotlib.pyplot as plt
import numpy as np
from pygmsh import *

import traceon.geometry as G
import traceon.excitation as E
import traceon.plotting as P
import traceon.solver as S
import traceon.tracing as T

import util

angle = 0.05
r1 = 7.5
r2 = 12.5

def create_geometry(MSF, symmetry, for_plot):
    """Create the spherical deflection analyzer from the following paper

    D. Cubric, B. Lencova, F.H. Read, J. Zlamal
    Comparison of FDM, FEM and BEM for electrostatic charged particle optics.
    1999.
    """
    with G.Geometry(symmetry) as geom:
         
        points = [
            [0, -r2],
            [0, -r1],
            [r1, 0],
            [0, r1],
            [0, r2],
            [r2, 0]
        ]
         
        points = [geom.add_point([p[0], 0, p[1]] if symmetry==G.Symmetry.THREE_D else p) for p in points]
        center = geom.add_point([0, 0, 0])
         
        l2 = geom.add_circle_arc(points[1], center, points[2])
        l3 = geom.add_circle_arc(points[2], center, points[3])
        
        l5 = geom.add_circle_arc(points[4], center, points[5])
        l6 = geom.add_circle_arc(points[5], center, points[0])
        
        if symmetry == G.Symmetry.RADIAL:
            geom.add_physical([l2, l3], 'inner')
            geom.add_physical([l5, l6], 'outer')
        elif symmetry == G.Symmetry.THREE_D:
            s1 = G.revolve_around_optical_axis(geom, [l2, l3])
            s2 = G.revolve_around_optical_axis(geom, [l5, l6], factor=0.5 if for_plot else 1.0)
            geom.add_physical(s1, 'inner')
            geom.add_physical(s2, 'outer')

        geom.set_mesh_size_factor(MSF)
        return geom.generate_mesh()


def compute_error(geom):
    exc = E.Excitation(geom)
    exc.add_voltage(inner=5/3, outer=3/5)
    
    field = S.solve_bem(exc)
    correct = -10/(2/cos(angle)**2 - 1)
    assert -12.5 <= correct <= 7.5 # Between spheres
     
    if geom.symmetry == G.Symmetry.RADIAL:
        bounds = ((-0.1, 12.5), (-12.5, 12.5))
        position = np.array([0.0, 10.0]) 
        vel = np.array([np.cos(angle), -np.sin(angle)])*0.5930969604919433
    else:
        bounds = ((-0.1, 12.5), (-0.1, 0.1), (-12.5, 12.5))
        position = np.array([0.0, 0.0, 10.0]) 
        vel = np.array([np.cos(angle), 0.0, -np.sin(angle)])*0.5930969604919433
     
    tracer = T.Tracer(field, bounds)
    times, pos = tracer(position, vel)
     
    if geom.symmetry == G.Symmetry.THREE_D:
        pos = pos[:, [0, 2]] # Throw away y axis
     
    r_final = T.axis_intersection(pos)
     
    print(f'Correct intersection: {correct:.8f}')
    print(f'Computed intersection: {r_final:.8f}')
     
    return exc.get_number_of_active_elements(), abs(r_final/correct - 1)

util.parser.description = '''Trace electrons through a spherical capacitor. After the electron traces an arc through the capacitor, its intersection
with the axis is compared with the exact values given in following paper (first benchmark test):

Comparison of FDM, FEM and BEM for electrostatic charged particle optics. D. Cubric , B. Lencova, F.H. Read, J. Zlamal. 1999.
'''

util.parse_validation_args(create_geometry, compute_error, inner='blue', outer='darkblue')
