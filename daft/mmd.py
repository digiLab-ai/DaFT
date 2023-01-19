import numpy as np

class RandomMMD:
    """
    RandomMMD is a class that uses the random Fourier features of Rahimi
    and Recht (2012) to compute the maximum Mean Discrepancy (MMD) between
    two empirical distributions X~P and Y~Q.

    Attributes
    ----------
    X : numpy.ndarray
        The reference empirical distribution.
    n_features : int
        The dimension of the feature space.
    n_dim : int
        The dimension of the input space.
    omega : numpy.ndarray
        Frequency matrix of n_features x n_dim, normal random variable.
    b : numpy.ndarray
        Phase vector of n_feaures x 1, uniform random variable.
        
    Methods
    ----------
    phi(X)
        Project X into the feature space.
    get_E_phi(X)
        Get the expectation (mean) of X in the feature space.
    predict(X)
        Make predictions of input X.
    get_mmd(Y)
        Get the approximate MMD of Y and self.X.
    """

    def __init__(self, X, n_features):
        """
        Parameters
        ----------
        X : numpy.ndarray
            The reference empirical distribution.
        n_features : int
            The dimension of the feature space.
        Returns
        ----------
        None
        """

        # set the reference empirical distribution.
        self.X = X
        
        # set the feature space dimension.
        self.n_features = n_features
        
        # set the dimension of the input space.
        self.n_dim = X.shape[1]
        
        # initialise the random Fourier feature coefficients.
        self.omega = np.random.normal(size=(self.n_features, self.n_dim))
        self.b = np.random.uniform(low=0, high=2*np.pi, size=(self.n_features,1))
        
        # compute the mean of the reference distribution in the feature space.
        self.E_phi_X = self.get_E_phi(X)
        
    def phi(self, X):
        """
        Parameters
        ----------
        X : numpy.ndarray
            A numpy array for which to compute the feature space.
        Returns
        ----------
        np.ndarray
        """

        # project to the features space.
        return np.sqrt(2/self.n_features)*np.cos(np.dot(self.omega, X.T) + self.b)
    
    def get_E_phi(self, X):
        """
        Parameters
        ----------
        X : numpy.ndarray
            A numpy array for which to compute the expectation (mean) of 
            X in the feature space.
        Returns
        ----------
        float
        """
        
        # compute the mean of the features space.
        return self.phi(X).mean(axis=1)
        
    def get_mmd(self, Y):
        """
        Parameters
        ----------
        Y : numpy.ndarray
            A numpy array for which to compute the approximate MMD with
            respect to self.X, the reference distribution.
        Returns
        ----------
        float
        """
        
        # compute the mean of the feature space.
        E_phi_Y =  self.get_E_phi(Y)
        
        # compute the norm between the mean of the reference distribution
        # and the input distribution.
        return np.linalg.norm(self.E_phi_X - E_phi_Y)

    def _get_mmd_ga(self, indices):
        Y = self.X[indices,:]
        return (self.get_mmd(Y),)
