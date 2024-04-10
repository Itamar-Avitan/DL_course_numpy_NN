#%% imports
import numpy as np
import math
from keras.datasets import mnist
from keras.utils import to_categorical
import time 
#%% forward propagation
def initialize_parameters(layers_dim):
    """
    input: 
        layers_dim: list containing the dimensions of each layer in the network    
    output: 
        W_b_dict: dictionary containing the parameters "W1", "b1", ..., "WL", "bL"
    """
    W_b_dict = {}
    for i in range(1,len(layers_dim)):
        #intialize the weight matrix with random values
        W_b_dict['W' + str(i)] = np.random.uniform(-(1 / np.sqrt(layers_dim[i])), 1 / np.sqrt(layers_dim[i]),
                                                  (layers_dim[i], layers_dim[i - 1]))
        #initialize the bias vector with zeros
        W_b_dict['b' + str(i)] = np.zeros((layers_dim[i], 1))
        
        #check the shape of the weight matrix and bias vector to ensure that they are correct
        assert(W_b_dict['W' + str(i)].shape == (layers_dim[i], layers_dim[i-1]))
        assert(W_b_dict['b' + str(i)].shape == (layers_dim[i], 1))
    return W_b_dict

def linear_forward(A,W,b):
    """
    input:
        A - activations of the previous layer (nparray)
        W - the weight matrix of the current layer (nparray)
        b - the bias vector of the current layer (nparray) 
    output:
        Z the linear input of the current layer for the activation function
        linear_cache  - a tuple containing A, W, b that will be used in the backward pass
    """
    Z = np.dot(W,A) + b  #linear input
    linear_cache = (A, W, b) #cache the values of A, W, b to be used in the backward pass

    #checking if the shape of Z is correct
    assert(Z.shape == (W.shape[0], A.shape[1]))
    return Z, linear_cache

def softmax(Z):
    """
    input:
        Z - the linear input of the current layer for the activation function (nparray)
    output:
        A - the output of the activation function (nparray)
        activation_cache -  a cache of Z that will be used in the backward pass
    """
    A = np.exp(Z) / np.sum(np.exp(Z), axis=0) #softmax activation function
    activation_cache = Z #cache the value of Z to be used in the backward pass
    return A, activation_cache

def relu(Z):
    """
    input:
    Z - linear component of the current layer for the activation function (nparray)
    output : 
    A - the output of the activation function (nparray)
    activation_cache - a cache of  Z that will be used in the backward pass
    """
    A  = np.maximum(0,Z) #relu activation function
    activation_cache = Z #cache the value of Z to be used in the backward pass
    #check if A has the same shape as Z
    assert(A.shape == Z.shape)
    return A, activation_cache

def linear_activation_forward(A_prev, W, b, activation):
    """
    input:
        A_prev - activations of the previous layer (nparray)
        W - the weight matrix of the current layer (nparray)
        b - the bias vector of the current layer (nparray)
        activation - the activation function to be used in this layer, a string: "softmax" or "relu"
        
    output:
        A - the output of the activations of the current layer (nparray)
        cache - a tuple containg the linear_cache and the activation_cache that will be used in the backward pass
    """
    Z,linear_cache = linear_forward(A_prev, W, b)
    if activation == "softmax":
        A, activation_cache = softmax(Z)
    elif activation == "relu":
        A, activation_cache = relu(Z)
    #check A has the right dimensions 
    assert(A.shape == (W.shape[0], A_prev.shape[1]))
    
    cache = (linear_cache, activation_cache) #cache the linear_cache and activation_cache to be used in the backward pass
    return A,cache

def L_model_forward(X, W_b_dict,use_batchnorm = False):
    """
    input:
        X - the input data ,shape (input size,number of sampels) (nparray)
        W_b_dict - dictionary containing the parameters "W1", "b1", ..., "WL", "bL"
        use_batchnorm  - a bollean flag to determine if batchnorm should be used or not(defult - False)
    output: 
        AL - the last post-activation value
        caches - a list of caches containing every cache of the cache objects generated by the linear forward function    
    """
    #forward propagation for [LINEAR -> RELU]*(L-1) -> LINEAR -> SOFTMAX
    A = X
    caches = []
    layers_num = len(W_b_dict)//2 #number of layers in the neural network
    for l in range(1,layers_num):
        A_prev = A 
        A, cache = linear_activation_forward(A_prev, W_b_dict['W' + str(l)], W_b_dict['b' + str(l)],
                                             activation ="relu")
        if use_batchnorm:
            A = batchnorm(A)
        caches.append(cache)
    #last layer post activatin calculation (AL)
    AL,cache = linear_activation_forward(A, W_b_dict['W' + str(l+1)], W_b_dict['b' + str(l+1)],
                                         activation= 'softmax')
    caches.append(cache)
    #check the shape of AL
    assert(AL.shape == (W_b_dict['W' + str(l+1)].shape[0],X.shape[1]))
    return AL, caches

def compute_cost(AL,Y):
    """
    input :
        AL - the last post-activation value (probablity vector of each class) (nparray)
        Y - the labels vector encoded as a one-hot matrix (nparray) 
    output:
        cost - the cross-entropy cost    
    """
    #checkuing that the labels and the predicted values have the same shape
    assert(AL.shape == Y.shape)
    epsilon = 1e-10 
    pred = np.clip(AL, epsilon, 1. - epsilon) #clip the values to avoid log(0)
    m = Y.shape[1] #number of samples
    cost = -1/m * np.sum(Y * np.log(pred)) #cross-entropy cost
    #checking the cost is a number not a matrix
    assert(cost.shape == ())
    
    return cost

def batchnorm(A):
    """
    input:
        A - the activation values of a given layer
    output:
        NA - the normalized activation values
    """

    means = np.mean(A.T, axis=0)
    std_vat = np.std(A.T, axis=0)
    NA  = (A.T - means) / (std_vat + 0.0001) #to avoid division by zero
    #check the shape of NA is the same as A
    assert(NA.T.shape == A.shape)
    
    return NA.T
#%% Backward Propagation
def linear_backward(dZ, cache):
    """
    input:
        dZ - the gradient of the cost with respect to the linear output of the current layer
        cache - a tuple containing A, W, b from the forward pass in the current layer
    output:
    dA_prev - the gradient of the cost with respect to the activation of the previous layer
    dW - the gradient of the cost with respect to W
    db - the gradient of the cost with respect to b  
    """
    A_prev,W,b  = cache
    m = A_prev.shape[1] #number of samples
    dA_prev = np.dot(W.T,dZ) #gradient of the cost with respect to the activation of the previous layer
    dW = 1/m * np.dot(dZ,A_prev.T) #gradient of the cost with respect to W
    db = 1/m * np.sum(dZ,axis=1,keepdims=True) #gradient of the cost with respect to b
    #checking the shape of dA_prev, dW, db
    assert(dA_prev.shape == A_prev.shape)
    assert(dW.shape == W.shape)
    assert(db.shape == b.shape)
    return dA_prev, dW, db

def linear_activation_backward(dA,cache,activation):
    """
    input:
        dA - post activation gradient of the current layer
        cache - a tuple containing the linear and activations cache
        activation - the activation function to be used
    output:
        dA_prev - the gradient of the cost with respect to the activation of the previous layer
        dW - the gradient of the cost with respect to W
        db - the gradient of the cost with respect to b
    
    """
    linear_cache,activation_cache = cache
    if activation == "relu":
        dZ = relu_backward(dA, activation_cache)
    elif activation == "softmax":
        dZ = softmax_backward(dA, activation_cache)
    
    dA_prev, dW, db = linear_backward(dZ, linear_cache)
    return dA_prev, dW, db

def relu_backward(dA, activation_cache):
    """
    input:
        dA - the post activation gradient 
        activation_cache - a cache of Z
    output:
        dZ - the gradient of the cost with respect to Z
    """
    dA[activation_cache <= 0] = 0 #gradient of the cost with respect to Z
    return dA

def softmax_backward(dA, activation_cache):
    """
    input:
        dA - the post activation gradient 
        activation_cache - a cache of Z
    output:
        dZ - the gradient of the cost with respect to Z
    """
    Z = activation_cache
    T = np.exp(Z)
    A = T / np.sum(T, axis=0)
    dZ  = dA * A * (1 - A) #gradient of the cost with respect to Z
    #checking the shape of dZ
    assert(dZ.shape == Z.shape)
    return dZ

def L_model_backward(AL, Y, caches):
    """
    input:
        AL - the last post-activation value contains the probablity vector of each class (nparray)
        Y - the labels vector encoded as a one-hot matrix(nparray)
        caches - a list of caches containing every cache of the cache objects both inear and activation caches
    output:
        grad - a dictionary containing the gradients of the cost with respect to W and b
    """
    num_layers = len(caches) #number of layers
    m = AL.shape[1] #number of samples
    grads = {}
    Y = Y.reshape(AL.shape) #reshape Y to have the same shape as AL
    #intialize the backpropagation
    dAL = - (np.divide(Y, AL) - np.divide(1 - Y, 1 - AL)) #gradient of the cost with respect to AL
    last_cache = caches[-1]
    #get the last layer gradients
    grads["dA" + str(num_layers)], grads["dW" + str(num_layers)], grads["db" + str(num_layers)] = linear_activation_backward(dAL, last_cache, activation = "softmax")
    
    
    for i in reversed(range(num_layers-1)):
        last_cache = caches[i]
        #caclulate the gradients of the cost with respect to W and b
        dA_prev_temp, dW_temp,db_temp = linear_activation_backward(grads["dA" + str(i + 2)], last_cache, 
                                                                   activation = "relu")
        #store the gradients in the grads dictionary
        grads["dA" + str(i + 1)],grads["dW" + str(i+1)],grads["db" + str(i+1)] = dA_prev_temp, dW_temp, db_temp
    return grads

def update_parameters(W_b_dict, grads, learning_rate,L2_norm = False):
    """
    input:
        W_b_dict - dictionary containing the parameters "W1", "b1", ..., "WL", "bL"
        grads - dictionary containing the gradients of the cost with respect to W and b
        learning_rate - the learning rate
        L2_norm -  bool that determines if L2 norm should be used or not
    output:
        W_b_dict - dictionary containing the updated parameters "W1", "b1", ..., "WL", "bL"
    
    """
    
    len_layers = len(W_b_dict)//2 #number of layers
    for l in range(1,len_layers+1):
        if L2_norm:
            W_b_dict["W"+str(l)] = W_b_dict["W"+str(l)] -learning_rate * (grads["dW" + str(l)] 
                                                                          + learning_rate * W_b_dict["W"+str(l)])
        else:
            W_b_dict["W"+str(l)] = W_b_dict["W"+str(l)] -learning_rate * grads["dW" + str(l)]
        W_b_dict["b"+str(l)] = W_b_dict["b"+str(l)] -learning_rate * grads["db" + str(l)]
    return W_b_dict

def L_layer_model(X,Y,layers_dims,learning_rate,num_iterations,batch_size,use_batchnorm = False,L2_norm = False):
    """
    input: 
        X - the input data ,shape (input size,number of sampels) (nparray)
        Y - the labels vector encoded as a one-hot matrix (nparray)
        layers_dims  - list containing the dimensions of each layer in the network
        learning_rate - the learning rate
        num_iterations - the number of iterations
        batch_size - the size of the batch
        use_batchnorm  - a bollean flag to determine if batchnorm should be used or not(defult - False)
        L2_norm -  bool that determines if L2 norm should be used or not(defult - False)
    output:
        W_b_dict - dictionary containing the parameters "W1", "b1", ..., "WL", "bL"
        costs - the values of the cost function 
    """
    X,Y = X.T,Y.T #transpose X and Y
    current_accuracy, prev_accuracy = 0, 0
    #radomly divide the data into training and testing sets
    indices  = np.random.permutation(X.shape[0])
    
    training_idx, test_idx = indices[:math.ceil(0.8*X.shape[0])], indices[math.ceil(0.8*X.shape[0]):]
    X_train,X_val = X[training_idx,:],X[test_idx,:]
    Y_train,Y_val = Y[training_idx,:],Y[test_idx,:]
    costs = [] #store the values of the cost function
    W_b_dict = initialize_parameters(layers_dims) #initialize the parameters
    batch_num = math.ceil(X_train.shape[0]/batch_size) #number of batches
    X_batches,Y_batches = [],[] #store the batches
    stop_sign = False #a flag to stop the training
    batch_so_far = 0 
    for i in range(batch_num):
        X_batches.append(X_train[i*batch_size:(i+1)*batch_size,:].T)
        Y_batches.append(Y_train[i*batch_size:(i+1)*batch_size,:].T)
    for i in range(num_iterations):
        if not stop_sign:
            for j in range(len(X_batches)):
                AL,caches = L_model_forward(X_batches[j],W_b_dict,use_batchnorm) #forward propagation
                grads = L_model_backward(AL,Y_batches[j],caches) #backward propagation
                W_b_dict = update_parameters(W_b_dict,grads,learning_rate,L2_norm) #update the parameters
                batch_so_far += 1
                if batch_so_far % 100 == 0:     
                    cost = compute_cost(AL,Y_batches[j]) #compute the cost]
                    if L2_norm:
                        for k in range(len(layers_dims)-1):
                            w = W_b_dict["W"+str(k+1)]
                            cost = cost + (learning_rate/2) * np.sum(w * w)
                    costs.append(cost)
                    print("iteration " + str(i+1) + f" the {batch_so_far} batch, cost = {cost}") #print the cost each 100 batches
            current_accuracy = predict(X_val.T,Y_val.T,W_b_dict,use_batchnorm) #predict the validation set
            if current_accuracy - prev_accuracy < 0.00000001  :#stop the training if the accuracy is not improving
                stop_sign = True
                break
            prev_accuracy = current_accuracy #update the previous accuracy
    #gets training and validation accuracy for the final model
    training_accuracy = predict(X.T,Y.T,W_b_dict,use_batchnorm)
    val_accuracy = predict(X_val.T,Y_val.T,W_b_dict,use_batchnorm)
    print(f"the training accuracy is {training_accuracy}, the validation accuracy is {val_accuracy}, it took "+str(i+1)+ f"iterations to train the model and {batch_so_far} batches")
    return W_b_dict,costs,training_accuracy,val_accuracy

def predict(X,Y,W_b_dict,use_batchnorm):
    """
    input:
        X - the input data ,shape (input size,number of sampels) (nparray)
        Y - the labels vector encoded as a one-hot matrix (nparray)
        W_b_dict - dictionary containing the parameters "W1", "b1", ..., "WL", "bL"
        use_batchnorm  - a bollean flag to determine if batchnorm should be used or not(defult - False)
    output:
        accuracy - the accuracy of the model on the given data
    """
    N_sampels = X.shape[1] #number of samples
    probs,_ = L_model_forward(X,W_b_dict,use_batchnorm) #forward propagation
    correct = np.sum(np.argmax(probs,keepdims=True,axis = 0) == np.argmax(Y,keepdims = True,axis = 0))
    accuracy = correct/N_sampels
    return accuracy

def preprocess_data(x, y):
    """
    Preprocess the MNIST data from Keras.
    Reshape to the appropriate matrix dimensions as per our network architecture.
    :param x: the raw pixel data
    :param y: the classification of the samples
    """
    x_flat = x.reshape(x.shape[0], -1).T / 255.
    y_pp = to_categorical(y, 10)
    y_pp = y_pp.reshape(y_pp.shape[0], -1).T

    return x_flat, y_pp

#%% run the model on the MNIST dataset

#define parameters 
learning_rate = 0.009
batch_size = 100
num_iterations = 100
use_batchnorm = False
L2_norm = False

#load the MNIST dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, y_train = preprocess_data(x_train, y_train)
x_test, y_test = preprocess_data(x_test, y_test)


layers_dims = [x_train.shape[0],20,7,5,10] #the dimensions of the layers in the network
#%% train and gets model accuracy without batchnorm or L2 norm
time_start_a = time.time()
W_b_dict_a,costs_a,training_accuracy_a,val_accuracy_a = L_layer_model(x_train, y_train, layers_dims,
                                                              learning_rate, num_iterations, batch_size, use_batchnorm, L2_norm)
end_time_a = time.time()
elapsed_time_a = end_time_a - time_start_a
test_accuracy_a = predict(x_test,y_test,W_b_dict_a,use_batchnorm)
        
#%% train and gets model accuracy with batchnorm
use_batchnorm = True
start_time_batchnorm = time.time()
W_b_dict_batchnorm,costs_batchnorm,training_accuracy_batchnorm,val_accuracy_batchnorm = L_layer_model(x_train, y_train, layers_dims,
                                                              learning_rate, num_iterations, batch_size, use_batchnorm, L2_norm)
end_time_batchnorm = time.time()
elapsed_time_batchnorm = end_time_batchnorm - start_time_batchnorm
test_accuracy_batchnorm = predict(x_test,y_test,W_b_dict_batchnorm,use_batchnorm)

#%% train and gets model accuracy with L2 norm
use_batchnorm = False
L2_norm = True
start_time_L2 = time.time()
W_b_dict_L2,costs_L2,training_accuracy_L2,val_accuracy_L2 = L_layer_model(x_train, y_train, layers_dims,
                                                              learning_rate, num_iterations, batch_size, use_batchnorm, L2_norm)
end_time_L2 = time.time()
elapsed_time_L2 = end_time_L2 - start_time_L2
test_accuracy_L2 = predict(x_test,y_test,W_b_dict_L2,use_batchnorm)

#%%prints the results
print("#################################################################################################################")
print("the results of the model without batchnorm or L2 norm")
print(f"train accuracy : {training_accuracy_a},validation accuracy is {val_accuracy_a}, test accuracy is {test_accuracy_a}")
print("#################################################################################################################")
print("the results of the model with batchnorm")
print(f"train accuracy : {training_accuracy_batchnorm},validation accuracy is {val_accuracy_batchnorm}, test accuracy is {test_accuracy_batchnorm}")
print("#################################################################################################################")
print("the results of the model with L2 norm")
print("#################################################################################################################")
print(f"train accuracy : {training_accuracy_L2},validation accuracy is {val_accuracy_L2}, test accuracy is {test_accuracy_L2}")
print(f"the time taken to train the model without batchnorm or L2 norm is {elapsed_time_a} seconds")
print(f"the time taken to train the model with batchnorm is {elapsed_time_batchnorm} seconds")
print(f"the time taken to train the model with L2 norm is {elapsed_time_L2} seconds")

weight_diff = np.sum(W_b_dict_a['W1'] - W_b_dict_L2['W1']) + np.sum(W_b_dict_a['W2'] - W_b_dict_L2['W2']) + np.sum(W_b_dict_a['W3'] - W_b_dict_L2['W3']) + np.sum(W_b_dict_a['W4'] - W_b_dict_L2['W4'])
print("the difference between the weights of the model without batchnorm or L2 norm and the model with L2 norm is " + str(weight_diff))