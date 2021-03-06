import numpy as np
import sys

from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

import Bayes,performanceAnalyser, Preprocessing
import kmeans
import KNN
import Visualization
import ROC

dists = {-1: "Ignore",0:"Gaussian", 1:"Multinomail"}

class Classifier:
	train_test_ratio = 0.8
	dataset_folder = 'Datasets'	

	def __init__(self,inputDataFileList,mode):
		self.mode = mode
		if mode == 0:
			self.Train, self.Test, self.Label = self.collectInputMedical(inputDataFileList)
		elif mode == 1:
			self.Train, self.Test, self.Label = self.collectInputFashion(inputDataFileList)
		else:
			self.Train, self.Test, self.Label = self.collectInputRailway(inputDataFileList)

	def collectInputMedical(self,inputDataFileList):
		
		labels = ['TEST1','TEST2','TEST3','Health']
		num_labels = len(labels)
		arrays = []

		for k in range(len(inputDataFileList)):
			file = inputDataFileList[k]
			with open(str(self.dataset_folder+'/'+ file),'r') as inputFile:
				lines = inputFile.readlines()
				lines = lines[1:]
				num_records= len(lines)
				arrays.append(np.zeros((num_records,num_labels),dtype=np.float64))
				for i in range(num_records):
					record = lines[i]
					if record.strip() == '':
						continue
					record = record.strip().split(',')
					for j in range(num_labels-1):
						arrays[k][i][j] = float(record[j+1])
					y_label = record[0]
					if y_label == 'HEALTHY':
						arrays[k][i][3] = 0
					elif y_label == 'MEDICATION':
						arrays[k][i][3] = 1
					elif y_label == 'SURGERY':
						arrays[k][i][3] = 2
					if arrays[k][i][3] == -1:
						print("Invalid treatment type detected at line "+int(index+2)+" in file "+str(k+1))
						exit()

		return arrays[0],arrays[1],labels


	def collectInputFashion(self,inputDataFileList):

		labels = ['pixel'+str(i+1) for i in range(784) ]
		labels.append('Class')
		num_labels = len(labels)
		arrays = []

		for k in range(len(inputDataFileList)):
			file = inputDataFileList[k]
			with open(str(self.dataset_folder+'/'+ file),'r') as inputFile:
				lines = inputFile.readlines()
				lines = lines[1:]
				num_records= len(lines)
				arrays.append(np.zeros((num_records,num_labels),dtype=np.int))
				for i in range(num_records):
					record = lines[i]
					if record.strip() == '':
						continue
					record = record.strip().split(',')
					for j in range(num_labels-1):
						arrays[k][i][j] = int(record[j+1])
					arrays[k][i][num_labels-1] = int(record[0])

		return arrays[0],arrays[1],labels


	def collectInputRailway(self,inputDataFileList):
		with open(inputDataFile,'r') as inputFile:
			lines = inputFile.readlines()
			lines = lines[1:]
			labels = ['caseID','budget','memberCount','preferredClass','sex','age','ifBoarded']
			num_labels = len(labels)
			num_records= len(lines)
			num_train = int(Classifier.train_test_ratio*num_records)
			num_test = num_records - num_train
			test_array = np.zeros((num_test,num_labels),dtype= np.int64)
			train_array = np.zeros((num_train,num_labels),dtype=np.int64)
			test_indices = np.sort(np.random.choice(num_records-1,num_test,replace=False))

			i=0
			for index in test_indices:
				record = lines[index]
				if record.strip() == '':
					continue
				record = record.strip().split(',')
				
				#Handling caseID
				test_array[i][0] = int(record[0])
				
				#Handling budget
				test_array[i][1] = int(record[2])
				
				#Handling memberCount
				test_array[i][2] = int(record[3])
				
				#Handling preferredClass
				if record[4] == 'FIRST_AC':
					test_array[i][3] = 1
				elif record[4] == 'SECOND_AC':
					test_array[i][3] = 2
				elif record[4] == 'THIRD_AC':
					test_array[i][3] = 3
				elif record[4] == 'NO_PREF':
					test_array[i][3] = 4
				else:
					print(record[4])
					print('Unknown preferredClass detected')
					exit()

				# Handling sex
				if record[5] == 'male':
					test_array[i][4] = 1
				elif record[5] == 'female':
					test_array[i][4] = 2
				elif record[5] == '':
					test_array[i][4] = 3
				else:
					print(record[5])
					print('Unknown sex detected')
					exit()

				# Handling age
				test_array[i][5] = int(record[6])

				#Handling ifBoarded
				test_array[i][6] = int(record[1])

				i+=1

			i=0
			for index in range(num_records):
				if index in test_indices:
					continue
				record = lines[index]
				if record.strip() == '':
					continue
				record = record.strip().split(',')
				#Handling caseID
				train_array[i][0] = int(record[0])
				
				#Handling budget
				train_array[i][1] = int(record[2])
				
				#Handling memberCount
				train_array[i][2] = int(record[3])
				
				#Handling preferredClass
				if record[4] == 'FIRST_AC':
					train_array[i][3] = 1
				elif record[4] == 'SECOND_AC':
					train_array[i][3] = 2
				elif record[4] == 'THIRD_AC':
					train_array[i][3] = 3
				elif record[4] == 'NO_PREF':
					train_array[i][3] = 4
				else:
					print(record[4])
					print('Unknown preferredClass detected')
					exit()

				# Handling sex
				if record[5] == 'male':
					train_array[i][4] = 1
				elif record[5] == 'female':
					train_array[i][4] = 2
				elif record[5] == '':
					train_array[i][4] = 3
				else:
					print(record[5])
					print('Unknown sex detected')
					exit()

				# Handling age
				train_array[i][5] = int(record[6])

				#Handling ifBoarded
				train_array[i][6] = int(record[1])

				i+=1
			return train_array,test_array,labels	


def performPCA(inputDataClass,reduced_columns):
	############################################## PCA Visualisation #############################################
	# #variance v/s n_components : Fashion MNIST
	# start = 10
	# stop = 500
	# step = 15
	# Visualization.var_vs_comp(inputDataClass.Train[:,:-1], start, stop, step)
	########################################################### PCA #############################################

	##### Our PCA ####
	pca = Preprocessing.PCA(inputDataClass.Train[:,:-1], k = reduced_columns, whiten = False)					##### Hyperparameter ####
	reduced_train = pca.reduce(inputDataClass.Train[:,:-1], True)
	inputDataClass.Train =  np.hstack((reduced_train,inputDataClass.Train[:,-1].reshape(-1,1)))
	print("train_data reduced. YAYAYAYA")
	print("Train data reduced to columns = "+str(reduced_train.shape[1]))
	reduced_test = pca.reduce(inputDataClass.Test[:,:-1], False)
	inputDataClass.Test =  np.hstack((reduced_test,inputDataClass.Test[:,-1].reshape(-1,1)))
	print("test_data reduced. YAYAYAYA")
	print("Test data reduced to columns = "+str(reduced_test.shape[1]))

	### SKlearn PCA #####
	# pca = PCA(n_components=80,whiten=False)
	# pca.fit(inputDataClass.Train[:,:-1])
	# reduced_train = pca.transform(inputDataClass.Train[:,:-1])
	# inputDataClass.Train =  np.hstack((reduced_train,inputDataClass.Train[:,-1].reshape(-1,1)))
	# reduced_test = pca.transform(inputDataClass.Test[:,:-1])
	# inputDataClass.Test =  np.hstack((reduced_test,inputDataClass.Test[:,-1].reshape(-1,1)))


def normalizeData(inputDataClass):
	######################################## Normalising Data ####################################
	normalizer = Preprocessing.Normalise()
	inputDataClass.Train = np.hstack((normalizer.scale(inputDataClass.Train[:,:-1],train=True),inputDataClass.Train[:,-1].reshape(-1,1)))
	inputDataClass.Test = np.hstack((normalizer.scale(inputDataClass.Test[:,:-1],train=False),inputDataClass.Test[:,-1].reshape(-1,1)))

def performVisualizations(inputDataClass):
	########################################### Visualizations ###################################################
	# Visualization.visualizeDataCCD(np.vstack((inputDataClass.Train,inputDataClass.Test)))

	# correlation_dict = performanceAnalyser.getCorrelationMatrix(inputDataClass.Train)
	# Visualization.visualizeCorrelation(correlation_dict)

	# Visualization.visualizeDataPoints(inputDataClass.Train)
	# Visualization.comp_vs_var_accuracy()
	pass

def performBayes(inputDataClass, drawPrecisionRecall = False, drawConfusion = False):
	"""################################# Bayes Classifier #############################################"""

	##Sklearn
	# print("\nSklearn Naive Bayes")
	# clf = GaussianNB()
	# clf.fit(inputDataClass.Train[:,:-1], inputDataClass.Train[:,-1])

	# Ypred = clf.predict(inputDataClass.Train[:,:-1])
	# Ytrue = inputDataClass.Train[:,-1]
	# print("Training Accuracy = "+str(performanceAnalyser.calcAccuracyTotal(Ypred,Ytrue)))

	# Ypred = clf.predict(inputDataClass.Test[:,:-1])
	# Ytrue = inputDataClass.Test[:,-1]
	# print("Testing Accuracy = "+str(performanceAnalyser.calcAccuracyTotal(Ypred,Ytrue)))


	print("\nMy Naive Bayes")
	bayesClassifier = Bayes.Bayes(isNaive = False, distribution =[0 for i in range(inputDataClass.Train.shape[1]-1)])
	# bayesClassifier = Bayes.Bayes(isNaive = True, distribution =[-1,0,0,1,1,0])
	bayesClassifier.train(inputDataClass.Train)
	print("Training of model done.")

	Ypred = bayesClassifier.fit(inputDataClass.Train)
	Ytrue = inputDataClass.Train[:,-1]
	print("Training Accuracy = "+str(performanceAnalyser.calcAccuracyTotal(Ypred,Ytrue)))

	Ypred = bayesClassifier.fit(inputDataClass.Test)
	Ytrue = inputDataClass.Test[:,-1]
	print("Testing Accuracy = "+str(performanceAnalyser.calcAccuracyTotal(Ypred,Ytrue)))

	print("Prediction done.")

	if drawConfusion:
		confusion = performanceAnalyser.getConfusionMatrix(Ytrue,Ypred)
		Visualization.visualizeConfusion(confusion)

	if drawPrecisionRecall:		
		############################ precision-recall curve #############################
		threshold = np.arange(0.9,0.1,-0.1)
		probas = bayesClassifier.get_probas()
		for dic in probas:
			sums=0.0
			for item in dic:
				sums+=dic[item]
			for item in dic:
				dic[item] = dic[item]/sums
		roc = ROC.Roc(Ytrue,probas,threshold,'')
		roc.Roc_gen()

		precision, recall, _ = precision_recall_curve(Ytrue, probas)

		plt.step(recall, precision, color='b', alpha=0.2, where='post')
		plt.fill_between(recall, precision, step='post', alpha=0.2,color='b')
		plt.xlabel('Recall')
		plt.ylabel('Precision')
		plt.ylim([0.0, 1.05])
		plt.xlim([0.0, 1.0])
		plt.title('Precision Recall Curve')

	return Ytrue,Ypred

def performKMeans(inputDataClass,k,mode,num_runs,visualize=False):
	covar = -1
	if mode == 3:
		covar = performanceAnalyser.getFullCovariance(inputDataClass.Train[:,:-1])
	labels, means, rms, Ypred = kmeans.kfit(inputDataClass.Train[:,:-1],k,inputDataClass.Train[:,-1],inputDataClass.Test[:,:-1],num_runs = num_runs, mode = mode,covar=covar)
	print("rms = "+str(rms))
	print("Kmeans done")

	Ytrue = inputDataClass.Test[:,-1]
	print("Testing Accuracy = "+str(performanceAnalyser.calcAccuracyTotal(Ypred,Ytrue)))

	if visualize:
		Visualization.visualizeKMeans(inputDataClass.Train[:,:-1],labels,k)
		print("Kmeans visualized")

	return Ytrue,Ypred

def performKNN(inputDataClass, nearestNeighbours,mode,label_with_distance=False):
	covar=-1
	if mode == 3:
		covar = performanceAnalyser.getFullCovariance(inputDataClass.Train[:,:-1])
	knn = KNN.KNN(nearestNeighbours,inputDataClass.Train[:,:-1],inputDataClass.Test[:,:-1],inputDataClass.Train[:,-1],label_with_distance=label_with_distance, mode=mode, covar=covar)
	knn.allocate()
	Ypred = knn.labels
	Ytrue = inputDataClass.Test[:,-1]

	print("Testing Accuracy = "+str(performanceAnalyser.calcAccuracyTotal(Ypred,Ytrue)))

	

if __name__ == '__main__': 
	if len(sys.argv) < 2:
		print("Invalid Format. Provide input file names")
		exit()
	inputDataFile = sys.argv[1]
	
	mode = -1		# 0 for Medical; 1 for Fashion; 2 for Railway

	mod_dict = {0:'Medical_data', 1:'fashion-mnist', 2:'railway_Booking'}

	if inputDataFile == 'Medical_data.csv':
		mode = 0
		x= []
		x.append(inputDataFile)
		if len(sys.argv) != 3:
			print('Enter both train and test files')
			exit()
		x.append(sys.argv[2])
		inputDataFile = x
	elif inputDataFile == 'fashion-mnist_train.csv':
		mode = 1
		x= []
		x.append(inputDataFile)
		if len(sys.argv) != 3:
			print('Enter both train and test files')
			exit()
		x.append(sys.argv[2])
		inputDataFile = x
	elif inputDataFile == 'railwayBookingList.csv':
		mode = 2

	if mode==-1:
		print("Unknown Dataset. Enter valid dataset.")
		exit()

	inputDataClass = Classifier(inputDataFile,mode)

	# Removes id from railway data
	if mode == 2:
		inputDataClass.Train = inputDataClass.Train[:,1:]
		inputDataClass.Test = inputDataClass.Test[:,1:]

	if mode == 1:
		"""################################# PCA #############################################"""
		reduced_columns = 80
		performPCA(inputDataClass = inputDataClass, reduced_columns = reduced_columns)	
	
	"""################################# Normalisation #############################################"""
	normalizeData(inputDataClass = inputDataClass)

	"""################################# Visualization #############################################"""
	# performVisualizations(inputDataClass = inputDataClass)

	"""################################# Bayes #############################################"""
	Ytrue,Ypred = performBayes(inputDataClass = inputDataClass, drawPrecisionRecall = False, drawConfusion = False)
	
	"""################################# KMEANS #############################################"""
	# k = 3					### Hyperparameter ###
	# mode = 0			# mode = {0 : Euclidean, 1: Manhattan, 2 : Chebyshev, 3: Mahalnobis}
	# num_runs= 100
	# Ytrue,Ypred = performKMeans(inputDataClass,k,mode,num_runs,visualize=False)

	"""################################# KNN #############################################"""

	# nearestNeighbours = 15	### Hyperparameter ###	
	# mode = 0		# mode = {0 : Euclidean, 1: Manhattan, 2 : Chebyshev}
	# performKNN(inputDataClass, nearestNeighbours,mode,label_with_distance=False)	

	"""###############################PRECISION-RECALL-F1##########################################"""
	# print(Ytrue)
	# print(Ypred)
	precision,recall, f1score = performanceAnalyser.goodness(Ytrue,Ypred)
	print("\nPrecision")
	print(precision)
	print("Recall")
	print(recall)
	print("F1 Score")
	print(f1score)