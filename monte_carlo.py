# Coded for Python 3.

# Produces Table 2, the simulation results.

import numpy as np, pandas as pd, nuclear_norm_module as nn, time
from scipy.spatial.distance import pdist, squareform

np.random.seed(seed=0)

Ns = [50,100,150,200,250,300,350,400] # sample sizes
B = 500                               # number of simulation draws

print('B = {}\n'.format(B))

##### Compute MSE of estimator #####

MSEs = np.zeros((3,len(Ns),B))  # mean-squared errors

for i,n in enumerate(Ns):
    for b in range(B):
        # latent space model
        alpha = np.random.normal(0,1,n)
        positions = np.random.exponential(size=(n,2))
        latent_index = alpha + alpha[:,None] - squareform(pdist(positions))
        P_LSM = np.exp(latent_index) / (1 + np.exp(latent_index)) # n x n matrix of link probabilities
        np.fill_diagonal(P_LSM,0) # zero diagonals
        U = np.random.uniform(0,1,size=(n,n))
        U = U.T/2 + U/2
        A_LSM = U < P_LSM # n x n adjacency matrix

        # random dot product graph
        positions = np.sqrt(np.random.uniform(0,1,n))
        P_RDP = positions * positions[:,None] # n x n matrix of link probabilities
        np.fill_diagonal(P_RDP,0) # zero diagonals
        U = np.random.uniform(0,1,size=(n,n))
        U = U.T/2 + U/2
        A_RDP = U < P_RDP # n x n adjacency matrix

        # stochastic block model
        P_SBM = np.ones((n,n))*0.3 # n x n matrix of link probabilities
        bs = int(n/5)
        for r in range(5): P_SBM[(r*bs):((r+1)*bs),(r*bs):((r+1)*bs)] = 0.7
        np.fill_diagonal(P_SBM,0) # zero diagonals
        U = np.random.uniform(0,1,size=(n,n))
        U = U.T/2 + U/2
        A_SBM = U < P_SBM # n x n adjacency matrix

        # generate k ARDs
        k = int(round(n**(0.4)))
        types = np.random.binomial(1,0.5,size=(k,n))
        ARD_LSM = types.dot(A_LSM) # k x n
        ARD_RDP = types.dot(A_RDP) # k x n
        ARD_SBM = types.dot(A_SBM) # k x n

        # estimation
        lmbd = 4*n*np.sqrt(k) # penalty

        start = time.time()
        Phat_LSM = nn.matrix_regression(ARD_LSM, types, lmbd)
        Phat_RDP = nn.matrix_regression(ARD_RDP, types, lmbd)
        Phat_SBM = nn.matrix_regression(ARD_SBM, types, lmbd)
        end = time.time()
        if b == 0: print('n = {}: {} seconds computation time.'.format(n,end-start))
        
        # mean-squared errors
        MSEs[0,i,b] = ((Phat_LSM - P_LSM)**2).mean()
        MSEs[1,i,b] = ((Phat_RDP - P_RDP)**2).mean()
        MSEs[2,i,b] = ((Phat_SBM - P_SBM)**2).mean()
        
##### Output results #####

print('\n\caption{Mean-Squared Error}')
table = pd.DataFrame(MSEs.mean(axis=2))
table.columns = Ns
table.index.rename('$n$', inplace=True)
table.index = ['LSM', 'RDP', 'SBM']
print(table.to_latex(float_format = lambda x: '%.5f' % x, header=True, escape=False))
