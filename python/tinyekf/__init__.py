'''
    Extended Kalman Filter in Python

    Copyright (C) 2016 Simon D. Levy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as 
    published by the Free Software Foundation, either version 3 of the 
    License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
'''

import numpy as np
from abc import ABCMeta, abstractmethod

class EKF(object):
    '''
    A abstrat class for the Extended Kalman Filter, based on the tutorial in
    http://home.wlu.edu/~levys/kalman_tutorial.
    '''
    __metaclass__ = ABCMeta

    def __init__(self, n, m, pval=0.1, qval=1e-4, rval=0.1):
        '''
        Creates a KF object with n states, m observables, and specified values for 
        prediction noise covariance pval, process noise covariance qval, and 
        measurement noise covariance rval.
        '''

        # No previous prediction noise covariance
        self.P_pre = None

        # Current state is zero, with diagonal noise covariance matrix
        self.x = _Vector(n)
        self.P_post = _Matrix.eye(n) * pval

        # Get state transition and measurement Jacobians from implementing class
        self.F = _Matrix.fromData(self.getF(self.x))
        self.H = _Matrix.fromData(self.getH(self.x))

        # Set up covariance matrices for process noise and measurement noise
        self.Q = _Matrix.eye(n) * qval
        self.R = _Matrix.eye(m) * rval
 
        # Identity matrix will be usefel later
        self.I = _Matrix.eye(n)

    def step(self, z):
        '''
        Runs one step of the EKF on observations z, where z is a tuple of length M.
        Returns a NumPy array representing the updated state.
        '''

        # Predict ----------------------------------------------------

        # $\hat{x}_k = f(\hat{x}_{k-1})$
        self.x = _Vector.fromData(self.f(self.x.data))

        # $P_k = F_{k-1} P_{k-1} F^T_{k-1} + Q_{k-1}$
        self.P_pre = self.F * self.P_post * self.F.transpose() + self.Q

        self.P_post = self.P_pre.copy()

        # Update -----------------------------------------------------

        # $G_k = P_k H^T_k (H_k P_k H^T_k + R)^{-1}$
        G = self.P_pre * self.H.transpose() * (self.H * self.P_pre * self.H.transpose() + self.R).invert()

        # $\hat{x}_k = \hat{x_k} + G_k(z_k - h(\hat{x}_k))$
        self.x += G * (_Vector.fromTuple(z) - _Vector.fromData(self.h(self.x.data)))

        # $P_k = (I - G_k H_k) P_k$
        self.P_post = (self.I - G * self.H) * self.P_pre

        return self.x.asarray()

    @abstractmethod
    def f(self, x):
        '''
        Your implementing class should define this method for the state transition function f(x).
        '''
        raise NotImplementedError()    

    @abstractmethod
    def getF(self, x):
        '''
        Your implementing class should define this method for returning the Jacobian F of the 
        state transition function.
        '''
        raise NotImplementedError()    

    @abstractmethod
    def h(self, x):
        '''
        Your implementing class should define this method for the observation function h(x).
        '''
        raise NotImplementedError()    

    @abstractmethod
    def getH(self, x):
        '''
        Your implementing class should define this method for returning the Jacobian H of the 
        observation function.
        '''
        raise NotImplementedError()    

# Linear Algebra support =============================================

class _Matrix(object):

    def __init__(self, r=0, c=0):

        self.data = np.zeros((r,c)) if r>0 and c>0 else None

    def __str__(self):

        return str(self.data) + " " + str(self.data.shape)

    def __mul__(self, other):

        new = _Matrix()

        if type(other).__name__ in ['float', 'int']:
            new.data = np.copy(self.data)
            new.data *= other
        else:
            new.data = np.dot(self.data, other.data)

        return new

    def __add__(self, other):

        new = _Matrix()
        new.data = self.data + other.data
        return new

    def __sub__(self, other):

        new = _Matrix()
        new.data = self.data - other.data
        return new

    def __setitem__(self, key, value):

        self.data[key] = value

    def __getitem__(self, key):

        return self.data[key]

    def asarray(self):

        return np.asarray(self.data[:,0])

    def copy(self):

        new = _Matrix()
        new.data = np.copy(self.data)
        return new

    def transpose(self):

        new = _Matrix()
        new.data = self.data.T
        return new

    def invert(self):

        new = _Matrix()
        try:
            new.data = np.linalg.inv(self.data)
        except Exception as e:
            print(self.data)
            print(e)
            exit(0)
        return new

    @staticmethod
    def eye(n, m=0):

        I = _Matrix()

        if m == 0:
            m = n

        I.data = np.eye(n, m)

        return I

    @staticmethod
    def fromData(data):

        a = _Matrix()

        a.data = data

        return a

class _Vector(_Matrix):

    def __init__(self, n=0):

        self.data = np.zeros((n,1)) if n>0 else None

    @staticmethod
    def fromTuple(t):

        v = _Vector(len(t))

        for k in range(len(t)):
            v[k] = t[k]

        return v


    @staticmethod
    def fromData(data):

        v = _Vector()

        v.data = data

        return v





