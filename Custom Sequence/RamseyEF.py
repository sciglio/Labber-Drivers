#!/usr/bin/env python3
import numpy as np
from copy import copy
from sequence import Sequence
from gates import Gate, VirtualZGate, CompositeGate, IdentityGate, CustomGate
from pulse import PulseShape, Pulse, PulseType

class CustomSequence(Sequence):
    def generate_sequence(self, config):
         """Generate sequence by adding gates/pulses to waveforms"""

         frequency = config.get('Parameter #1')
         amplitude = config.get('Parameter #2')
         width = config.get('Parameter #3')
         plateau = config.get('Parameter #4')
         shapeID=config.get('Parameter #5') # (0) gaussian, (1) cosine
         waitTime=config.get('Parameter #10')
         self.add_gate_to_all(Gate.Xp)

         pulse12 = Pulse()
         pulse12.width = width
         pulse12.plateau = plateau
         pulse12.amplitude = amplitude
         pulse12.frequency = frequency
         if shapeID==0:
             pulse12.shape=PulseShape.GAUSSIAN
         if shapeID==1:
             pulse12.shape=PulseShape.COSINE
         pulse12.pulse_type=PulseType.XY
         pulse12.phase = 0
         gateP = CustomGate(pulse12)
         wait=Pulse()
         wait.shape=PulseShape.COSINE
         wait.width = 0
         wait.plateau = waitTime
         wait.amplitude = 0
         wait.frequency = 0
         gateWait=CustomGate(wait)
         self.add_gate_to_all(gateP)
         self.add_gate_to_all(gateWait)
         self.add_gate_to_all(gateP)


         # self.add_gate_to_all(Gate.Xp)
