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
         drag_coeff= config.get('Parameter #5') #(drag coefficient)
         shapeID=config.get('Parameter #6') # (0) gaussian, (1) cosine
         pulse_train=config.get('Parameter #7') #yes (1) or no (0) for multiple alternate pulses for optimizing drag and Pi pulse
         N_pulses=config.get('Parameter #8') #ignored if pulse_train == 0
         self.add_gate_to_all(Gate.Xp)

         pulse12 = Pulse()
         pulse12n = Pulse()
         pulse12.width = width
         pulse12n.width = width
         pulse12.plateau = plateau
         pulse12n.plateau = plateau
         pulse12.amplitude = amplitude
         pulse12n.amplitude = amplitude
         pulse12.frequency = frequency
         pulse12n.frequency = frequency
         if shapeID==0:
             pulse12.shape=PulseShape.GAUSSIAN
             pulse12n.shape=PulseShape.GAUSSIAN
         if shapeID==1:
             pulse12.shape=PulseShape.COSINE
             pulse12n.shape=PulseShape.COSINE
         pulse12.use_drag = True
         pulse12n.use_drag = True
         pulse12.drag_coefficient = drag_coeff
         pulse12n.drag_coefficient = drag_coeff
         pulse12.pulse_type=PulseType.XY
         pulse12n.pulse_type=PulseType.XY
         pulse12.phase = 0
         pulse12n.phase = -np.pi
         gateP = CustomGate(pulse12)
         gateN = CustomGate(pulse12n)
         if pulse_train:
             for i in range(int(N_pulses)):
                 if ((i % 2) == 0):
                     self.add_gate_to_all(gateP)
                 else:
                     self.add_gate_to_all(gateN)
         else:
             self.add_gate_to_all(gateP)

         # self.add_gate_to_all(Gate.Xp)
