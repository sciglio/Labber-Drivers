import InstrumentDriver
import numpy as np

class Driver(InstrumentDriver.InstrumentWorker):

    def performOpen(self, options={}):
        pass

    def performClose(self, bError=False, options={}):
        pass

    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        return value

    def performGetValue(self, quant, options={}):
        if quant.name=='Set data':
            x_min=self.getValue('start x')
            x_max=self.getValue('stop x')
            y_value=self.getValue('y value')
            Xpoints=int(self.getValue('Number of X points'))
            maxIter=int(self.getValue('Maximum iteration'))

            X=np.linspace(x_min, x_max, Xpoints)

            Z=np.zeros(X.shape, np.complex64)
            N=np.zeros(X.shape, np.int64)

            for m in range(Xpoints):
                n=0
                while np.abs(Z[m])<=2.0 and n<maxIter:
                    Z[m]=Z[m]**2+X[m]+1j*y_value
                    N[m]=n
                    n=n+1


            dataVector=N

            trace=quant.getTraceDict(dataVector, x0=x_min, dx=X[1]-X[0])

            return trace
        else:
            return quant.getValue()
