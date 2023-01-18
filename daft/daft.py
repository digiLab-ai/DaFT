from .mmd import RandomMMD
from .ga import IndexSelectionGA

class DaFT:
    def __init__(self, P, n_sub, n_features=None, **kwargs):
        
        self.P = P
        self.n_sub = n_sub
        self.n_total = self.P.shape[0]
        
        if n_features is None:
            n_features = P.shape[1]*1000
        
        self.n_features = n_features
        
        self.mmd = RandomMMD(self.P, self.n_features)
        
        self.ga = IndexSelectionGA(self.n_sub, 
                                   self.n_total, 
                                   self.mmd._get_mmd_ga, 
                                   **kwargs)
        
    def run(self, **kwargs):
        kwargs["k"] = 1
        
        indices = self.ga.run(**kwargs)[0]
        
        return self.P[indices,:]
