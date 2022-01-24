#! /usr/bin/env python

"""
Module with functions related to image coordinates and coordinate conversions.
"""

__author__ = 'Carlos Alberto Gomez Gonzalez, Valentin Christiaens'
__all__ = ['dist',
           'dist_matrix',
           'frame_center',
           'cart_to_pol',
           'pol_to_cart',
           'radial_to_eq',
           'QU_to_QUphi']

import math
from matplotlib.pyplot import xlim, ylim, axes, gca, show
import matplotlib.pyplot as plt
import numpy as np


def dist(yc, xc, y1, x1):
    """
    Return the Euclidean distance between two points, or between an array 
    of positions and a point.
    """
    return np.sqrt(np.power(yc-y1,2) + np.power(xc-x1,2))


def dist_matrix(n, cx=None, cy=None):
    """
    Create matrix with euclidian distances from a reference point (cx, cy).

    Parameters
    ----------
    n : int
        output image shape is (n, n)
    cx,cy : float
        reference point. Defaults to the center.

    Returns
    -------
    im : ndarray with shape (n, n)

    Notes
    -----
    This is a replacement for ANDROMEDA's DISTC.

    """
    if cx is None:
        cx = (n - 1) / 2
    if cy is None:
        cy = (n - 1) / 2

    yy, xx = np.ogrid[:n, :n]
    return np.sqrt((yy-cy)**2 + (xx-cx)**2)


def frame_center(array, verbose=False):
    """
    Return the coordinates y,x of the frame(s) center.
    If odd: dim/2-0.5
    If even: dim/2

    Parameters
    ----------
    array : 2d/3d/4d numpy ndarray
        Frame or cube.
    verbose : bool optional
        If True the center coordinates are printed out.

    Returns
    -------
    cy, cx : int
        Coordinates of the center.

    """
    if array.ndim == 2:
        shape = array.shape
    elif array.ndim == 3:
        shape = array[0].shape
    elif array.ndim == 4:
        shape = array[0, 0].shape
    else:
        raise ValueError('`array` is not a 2d, 3d or 4d array')

    cy = shape[0] / 2
    cx = shape[1] / 2

    if shape[0]%2:
        cy-=0.5
    if shape[1]%2:
        cx-=0.5        

    if verbose:
        print('Center px coordinates at x,y = ({}, {})'.format(cx, cy))  
    
    return int(cy), int(cx)


def cart_to_pol(x, y, cx=0, cy=0, north_convention=False):
    """
    Returns polar coordinates for input cartesian coordinates
    
    
    Parameters
    ----------
    x : float or numpy ndarray
        x coordinates with respect to the center
    y : float or numpy ndarray
        y coordinates with respect to the center
    cx, cy : float or numpy ndarray
        x, y coordinates of the center of the image to be considered for 
        conversion to cartesian coordinates.
    north_convention: bool
        Whether to use angles measured from North up/East left (True), or
        measured from the positive x axis (False).
        
    Returns
    -------
    r, theta: floats or numpy ndarrays
        radii and polar angles corresponding to the input x and y.
    """
    
    r = dist(cy,cx,y,x)
    theta = np.rad2deg(np.arctan2(y-cy,x-cx))
    if north_convention:
        theta -= 90
    
    return r, theta


def pol_to_cart(r, theta, cx=0, cy=0):
    """
    Returns cartesian coordinates for input polar coordinates
    
    Parameters
    ----------
    r, theta : float or numpy ndarray
        radii and polar angles (trigonometric) corresponding to the input
        x and y.
    cx, cy : float or numpy ndarray
        x, y coordinates of the center of the image to be considered for 
        conversion to cartesian coordinates.

    Returns
    -------
    x, y: floats or numpy ndarrays
        x, y coordinates corresponding to input radii and polar (trigonotetric)
        angles.
    """
    
    x = cx+r*np.cos(np.deg2rad(theta))
    y = cy+r*np.sin(np.deg2rad(theta))
    
    return x, y


def radial_to_eq(r=1, t=0, rError=0, tError=0, plot=False):
    """ 
    Convert the position given in (r,t) into \delta RA and \delta DEC, as 
    well as the corresponding uncertainties. 
    t = 0 deg (resp. 90 deg) points toward North (resp. East).   

    Parameters
    ----------
    r: float
        The radial coordinate.
    t: float
        The angular coordinate.
    rError: float
        The error bar related to r.
    tError: float
        The error bar related to t.
    plot: boolean, optional
        If True, a figure illustrating the error ellipse is displayed.
        
    Returns
    -------
    out : tuple
        ((RA, RA error), (DEC, DEC error))
                              
    """  
    ra = (r * np.sin(math.radians(t)))
    dec = (r * np.cos(math.radians(t)))   
    u, v = (ra, dec)
    
    nu = np.mod(np.pi/2-math.radians(t), 2*np.pi)
    a, b = (rError,r*np.sin(math.radians(tError)))

    beta = np.linspace(0, 2*np.pi, 5000)
    x, y = (u + (a * np.cos(beta) * np.cos(nu) - b * np.sin(beta) * np.sin(nu)),
            v + (b * np.sin(beta) * np.cos(nu) + a * np.cos(beta) * np.sin(nu)))
    
    raErrorInf = u - np.amin(x)
    raErrorSup = np.amax(x) - u
    decErrorInf = v - np.amin(y)
    decErrorSup = np.amax(y) - v        

    if plot:        
        plt.plot(u,v,'ks',x,y,'r')
        plt.plot((r+rError) * np.cos(nu), (r+rError) * np.sin(nu),'ob',
             (r-rError) * np.cos(nu), (r-rError) * np.sin(nu),'ob')
        plt.plot(r * np.cos(nu+math.radians(tError)), 
             r*np.sin(nu+math.radians(tError)),'ok')
        plt.plot(r * np.cos(nu-math.radians(tError)), 
             r*np.sin(nu-math.radians(tError)),'ok')
        plt.plot(0,0,'og',np.cos(np.linspace(0,2*np.pi,10000)) * r, 
             np.sin(np.linspace(0,2*np.pi,10000)) * r,'y')
        plt.plot([0,r*np.cos(nu+math.radians(tError*0))],
             [0,r*np.sin(nu+math.radians(tError*0))],'k')
        axes().set_aspect('equal')
        lim = np.amax([a,b]) * 2.
        xlim([ra-lim,ra+lim])
        ylim([dec-lim,dec+lim])
        gca().invert_xaxis()
        show()
        
    return ((ra,np.mean([raErrorInf,raErrorSup])),
            (dec,np.mean([decErrorInf,decErrorSup])))


def QU_to_QUphi(Q, U, delta_x=0, delta_y=0, scale_r2=False, 
                north_convention=False):
    """
    Returns Qphi and Uphi images, from input Q and U images.
    
    Parameters
    ----------
    Q: numpy ndarray
        2d numpy array containing the Q component of polarisation.
    U: numpy ndarray
        2d numpy array containing the U component of polarisation. Should have
        the same dimensions as Q.
    delta_x, delta_y: float, opt
        If the star is not at the center of the image, delta_x and delta_y 
        indicate by how much it is offset along the x and y dimensions, resp.
    scale_r2: bool, opt
        Whether to scale by r^2 during conversion.
    north_convention: bool, opt
        Whether to use angles measured from North up/East left (True), or
        measured from the positive x axis (False).
        
    Returns
    -------
    Qphi, Uphi: numpy ndarrays
        Qphi and Uphi images
    """
    
    cy,cx = frame_center(Q)
    Qphi = np.zeros_like(Q)
    Uphi = np.zeros_like(U)
    for ii in range(Q.shape[1]):
        for jj in range(Q.shape[0]):
            x = float(ii-cx-delta_x)
            y = float(jj-cy-delta_y)
            rho, phi = cart_to_pol(x, y, north_convention=north_convention)
            phi = np.deg2rad(phi)
            if scale_r2:
                Qphi[jj,ii] = (Q[jj,ii]*np.cos(2*phi) + 
                                U[jj,ii]*np.sin(2*phi))*rho**2
                Uphi[jj,ii] = (-Q[jj,ii]*np.sin(2*phi) + 
                                U[jj,ii]*np.cos(2*phi))*rho**2
            else:
                Qphi[jj,ii] = Q[jj,ii]*np.cos(2*phi) + U[jj,ii]*np.sin(2*phi)
                Uphi[jj,ii] = -Q[jj,ii]*np.sin(2*phi) + U[jj,ii]*np.cos(2*phi)
                
    return Qphi, Uphi