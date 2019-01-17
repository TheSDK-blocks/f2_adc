# f2_adc class 
# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 03.08.2018 11:12
import numpy as np
import tempfile
import subprocess
import shlex
import time

from refptr import *
from thesdk import *

#Simple buffer template
class f2_adc(thesdk):
    def __init__(self,*arg): 
        self.proplist = ['Rs', 'full_scale', 'Nbits']    #properties that can be propagated from parent
        self.Rs = 1000e6  # input sampling frequency
        self.full_scale = 1  # input is from -full_scale/2 to +full_scale/2 for min and max adc code
        self.Nbits = 3  # number of bits in the adc quantization
        self.iptr_A = IO();
        self.model='py';             #can be set externally, but is not propagated
        self._Z = IO();
        self._classfile=__file__
        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;
    def init(self):
        pass

    def run(self,*arg):
        if np.amax(np.abs(self.iptr_A.Data))>self.full_scale/2.0:
            self.print_log(type='W', msg="ADC is clipping with absolute value %s that is more than %s."%(np.amax(np.abs(self.iptr_A.Data)),self.full_scale/2.0))

        if len(arg)>0:
            par=True      #flag for parallel processing
            queue=arg[0]  #multiprocessing.Queue as the first argument
        else:
            par=False

        if self.model=='py':
            input_signal = np.array(self.iptr_A.Data)

            #input_delta = self.full_scale/(2**self.Nbits-1)
            input_delta = self.full_scale/(2*(2**(self.Nbits-1)-1))
            #input_quantized = input_delta*np.round((input_signal + self.full_scale/2)/input_delta)
            input_quantized = np.round(input_signal/input_delta)
            #input_quantized[np.where(input_quantized > self.full_scale)] = self.full_scale
            input_quantized[np.where(input_quantized > 2**(self.Nbits-1)-1)] =  2**(self.Nbits-1)-1
            input_quantized[np.where(input_quantized <  -(2**(self.Nbits-1)-1))] = -(2**(self.Nbits-1)-1) 


            #out = (input_quantized - self.full_scale/2)*(2**(self.Nbits-1)-1)
            out = input_quantized

            if par:
                queue.put(out)
            self._Z.Data=out
        else: 
            self.print_log(type='F', msg='Model %s not supported' %(self.model))
