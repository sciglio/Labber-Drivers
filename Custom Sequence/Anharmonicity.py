#!/usr/bin/env python3
import numpy as np
from copy import copy
from sequence import Sequence
from gates import Gate, VirtualZGate, CompositeGate, IdentityGate, CustomGate
from pulse import PulseShape, Pulse

class CustomSequence(Sequence):
    def generate_sequence(self, config):
         """Generate sequence by adding gates/pulses to waveforms"""

         frequency = config.get('Parameter #1')
         amplitude = config.get('Parameter #2')
         width = config.get('Parameter #3')
         plateau = config.get('Parameter #4')
         self.add_gate_to_all(Gate.Xp)

         pulse12 = Pulse()
         pulse12.truncation_range = 3
         pulse12.width = width
         pulse12.plateau = plateau
         pulse12.amplitude = amplitude
         pulse12.frequency = frequency
         gate = CustomGate(pulse12)
         self.add_gate_to_all(gate)
         # self.add_gate_to_all(Gate.Xp)
