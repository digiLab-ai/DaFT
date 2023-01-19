from .mmd import RandomMMD
from .ga import IndexSelectionGA

class DaFT:
    """
    DaFT is a class that implements the DerivAtive-Free Thinning algorithm.

    Attributes
    ----------
    X : numpy.ndarray
        The reference empirical distribution.
    n_total : int
        The number of datapoints in the reference distribution.
    n_sub : int
        The required number of datapoints for the thinned distribution.
    n_features : int
        The dimension of the feature space. 
    mmd : daft.mmd.RandomMMD
        An instance of daft.mmd.RandomMMD.
    ga : daft.ga.IndexSelectionGA
        An instance of daft.ga.IndexSelectionGA.
        
    Methods
    ----------
    run(**kwargs)
        Run the DaFT algorithm.
    """

    def __init__(self, X, n_sub, n_features=None, **kwargs):
        """
        Parameters
        ----------
        X : numpy.ndarray
            The reference empirical distribution.
        n_sub : int
            The required number of datapoints for the thinned distribution.
        n_features : int, optional
            The dimension of the feature space. Default is 1000 x input 
            dimension.
        kwargs
            Keyword arguments passed to daft.ga.IndexSelectionGA.
        Returns
        ----------
        None
        """
        
        # set the reference distribution.
        self.X = X
        
        # set the number of datapoints in the reference distribution.
        self.n_total = self.X.shape[0]
        
        # set the required size of the thinned distribution.
        self.n_sub = n_sub
        
        # compute the feature space dimension of it's not provided.
        if n_features is None:
            n_features = X.shape[1]*1000
        
        # set the feature space dimension.
        self.n_features = n_features
        
        # set up an MMD instance.
        self.mmd = RandomMMD(self.X, self.n_features)
        
        # set up a GA instance.
        self.ga = IndexSelectionGA(self.n_sub, 
                                   self.n_total, 
                                   self.mmd._get_mmd_ga, 
                                   **kwargs)
        
    def run(self, **kwargs):
        """
        Run DaFT.
        
        Parameters
        ----------
        kwargs
             Keyword arguments passed to daft.ga.IndexSelectionGA.run().
            
        Returns
        ----------
        numpy.ndarray
        """
        
        # set the number of chromosomes to return from the GA.
        kwargs["k"] = 1
        
        # run the GA.
        indices = self.ga.run(**kwargs)[0]
        
        # return the thinned distribution.
        return self.X[indices,:]
