import numpy as np
import math
import operator as op

# x is a data point
def gaussian(x, mu, sigma):
	p = (( maths.fabs(np.linalg.det(sigma)) * ((2*math.pi)**x.shape[1]))**(-0.5)) \
	* (np.exp( np.matmul(np.matmul(-0.5 * np.transpose(x-mu), np.linalg.inv(sigma)),  (x-mu) )))
	return p


# X is the whole feature vector consisting of ALL data points
# returns dictionaries mu, sigma  and list of labels 
def gaussian_mle(X, naive):
	# if input is both X and Y, make Y as last column of X
	N = X.shape[0]	
	# sorting according to Y
	X = X[X[:,X.shape[1]-1].argsort()]

	# slicing matrix acc. to classes
	sliced_matrix = {}

	x = X[0][len(X[0])-1]
	last_index = 0
	for i in range(1, X.shape[0]):
	    elem = X[i]
	    q = elem[len(elem)-1]
	    if q!= x:
	        sliced_matrix[x] = X[last_index:i, :X.shape[1]-1]
	        last_index = i
	    x = q
	sliced_matrix[x] = X[last_index:X.shape[0], :X.shape[1]-1]
	
	# parameters for each class 
	mu = {}

	for label, label_features in sliced_matrix.items():
		# total data points of this class
		total_pnts = label_features.shape[0]
		# mu vector for this class
		mu[label] = np.asarray(label_features.sum(axis = 0))/total_pnts
		# subtract mu from each row for sigma computation. . . 
		for i in range(label_features.shape[0]):
		    label_features[i] = label_features[i] - mu[label]


	sigma = {}
	# for every feature in X
	for label, label_features in sliced_matrix.items():
		# total data points of this class
		total_pnts = label_features.shape[0]
		sigma[label] = np.zeros(shape=(label_features.shape[1], label_features.shape[1]), dtype = np.float)
		for i in range(label_features.shape[1]):
			# for every feature in X starting from ith index
			for j in range(i, label_features.shape[1]):
				# for every data point
				sum = 0
				for k in range(label_features.shape[0]):
				# multiply
					if naive and i==j:
						sum += label_features[k][j]*label_features[k][i]
					else:
						sum += label_features[k][j]*label_features[k][i]
				if naive:
					if i==j:
						sigma[label][i][j] = (sum*1.0)/total_pnts
					else:
						sigma[label][i][j] = 0
				else:
					sigma[label][i][j] = (sum*1.0)/total_pnts

	return mu, sigma



def binomial( x, n, p):
	p = (ncr(n, x))*(p**x)((1-p)**(n-x))
	return p

def binomial_mle(X):
	pass

def bernoulli( x, p):
	p = (p**x)*((1-p)**(1-x))
	return p


def uniform( a, b):
	p = 1//(b-a)
	return p


def exponential( x, lamda):
	if x < 0:
		return 0
	else:
		p = lamda*(np.exp()**(-1*lamda*))


def poisson( x, lamda):
	p = (math.exp(-1*lamda)*(lamda**x))/math.factorial(x)
	return p


def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, xrange(n, n-r, -1), 1)
    denom = reduce(op.mul, xrange(1, r+1), 1)
    return numer/denom