# f2_adc class 
# Last modification by Marko Kosunen, marko.kosunen@aalto.fi, 12.04.2018 20:04
import numpy as np
import tempfile
import subprocess
import shlex
import time

from refptr import *
from thesdk import *
from rtl import *

#Simple buffer template
class f2_adc(rtl,thesdk):
    def __init__(self,*arg): 
        self.proplist = ['Rs', 'full_scale', 'Nbits']    #properties that can be propagated from parent
        self.Rs = 1000e6  # input sampling frequency
        self.full_scale = 1  # input is from -full_scale/2 to +full_scale/2 for min and max adc code
        self.Nbits = 3  # number of bits in the adc quantization
        self.iptr_A = refptr();
        self.model='py';             #can be set externally, but is not propagated
        self._Z = refptr();
        self._classfile=__file__
        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;
    def init(self):
        pass
        # self.def_rtl()
        # rndpart=os.path.basename(tempfile.mkstemp()[1])
        # self._infile=self._rtlsimpath +'/A_' + rndpart +'.txt'
        # self._outfile=self._rtlsimpath +'/Z_' + rndpart +'.txt'
        # self._rtlcmd=self.get_rtlcmd()

    # def get_rtlcmd(self):
    #     #the could be gathered to rtl class in some way but they are now here for clarity
    #     submission = ' bsub -q normal '
    #     rtllibcmd =  'vlib ' +  self._workpath + ' && sleep 2'
    #     rtllibmapcmd = 'vmap work ' + self._workpath
    #
    #     if (self.model is 'vhdl'):
    #         rtlcompcmd = ( 'vcom ' + self._rtlsrcpath + '/' + self._name + '.vhd '
    #                       + self._rtlsrcpath + '/tb_'+ self._name+ '.vhd' )
    #         rtlsimcmd =  ( 'vsim -64 -batch -t 1ps -g g_infile=' +
    #                        self._infile + ' -g g_outfile=' + self._outfile
    #                        + ' work.tb_' + self._name + ' -do "run -all; quit -f;"')
    #         rtlcmd =  submission + rtllibcmd  +  ' && ' + rtllibmapcmd + ' && ' + rtlcompcmd +  ' && ' + rtlsimcmd
    #
    #     elif (self.model is 'sv'):
    #         rtlcompcmd = ( 'vlog -work work ' + self._rtlsrcpath + '/' + self._name + '.sv '
    #                        + self._rtlsrcpath + '/tb_' + self._name +'.sv')
    #         rtlsimcmd = ( 'vsim -64 -batch -t 1ps -voptargs=+acc -g g_infile=' + self._infile
    #                       + ' -g g_outfile=' + self._outfile + ' work.tb_' + self._name  + ' -do "run -all; quit;"')
    #
    #         rtlcmd =  submission + rtllibcmd  +  ' && ' + rtllibmapcmd + ' && ' + rtlcompcmd +  ' && ' + rtlsimcmd
    #
    #     else:
    #         rtlcmd=[]
    #     return rtlcmd

    def run(self,*arg):
        if np.amax(np.abs(self.iptr_A.Value))>self.full_scale/2.0:
            self.print_log({'type':'W', 'msg':"ADC is clipping with absolute value %s that is more than %s."%(np.amax(np.abs(self.iptr_A.Value)),self.full_scale/2.0)} )

        if len(arg)>0:
            par=True      #flag for parallel processing
            queue=arg[0]  #multiprocessing.Queue as the first argument
        else:
            par=False

        if self.model=='py':
            input_signal = np.array(self.iptr_A.Value)

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
            self._Z.Value=out
        else: 
          try:
              os.remove(self._infile)
          except:
              pass
          fid=open(self._infile,'wb')
          np.savetxt(fid,np.transpose(self.iptr_A.Value),fmt='%.0f')
          #np.savetxt(fid,np.transpose(inp),fmt='%.0f')
          fid.close()
          while not os.path.isfile(self._infile):
              #print("Wait infile to appear")
              time.sleep(1)
          try:
              os.remove(self._outfile)
          except:
              pass
          print("Running external command \n", self._rtlcmd , "\n" )
          subprocess.call(shlex.split(self._rtlcmd));
          
          while not os.path.isfile(self._outfile):
              #print("Wait outfile to appear")
              time.sleep(1)
          fid=open(self._outfile,'r')
          #fid=open(self._infile,'r')
          #out = .np.loadtxt(fid)
          out = np.transpose(np.loadtxt(fid))
          fid.close()
          if par:
              queue.put(out)
          self._Z.Value=out
          os.remove(self._infile)
          os.remove(self._outfile)
