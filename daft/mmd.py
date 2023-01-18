import numpy as np

class RandomMMD:
    def __init__(self, P, n_features):

        self.P = P
        self.n_features = n_features
        self.n_dim = P.shape[1]
        
        self.omega = np.random.normal(size=(self.n_features, self.n_dim))
        self.b = np.random.uniform(low=0, high=2*np.pi, size=(self.n_features,1))
        
        self.E_phi_P = self.get_E_phi(P)
        
    def phi(self, x):
        return np.sqrt(2/self.n_features)*np.cos(np.dot(self.omega, x.T) + self.b)
    
    def get_E_phi(self, X):
        return self.phi(X).mean(axis=1)
        
    def get_mmd(self, Q):
        E_phi_Q =  self.get_E_phi(Q)
        return np.linalg.norm(self.E_phi_P - E_phi_Q)

    def _get_mmd_ga(self, indices):
        Q = self.P[indices,:]
        return (self.get_mmd(Q),)
