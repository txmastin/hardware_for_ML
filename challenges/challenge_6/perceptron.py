import numpy as np

# NAND training data
X = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])
y = np.array([1, 1, 1, 0])  # NAND outputs



weights = np.random.randn(2)  
bias = np.random.randn()
learning_rate = 0.1
epochs = 5000  

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return sigmoid(x) * (1 - sigmoid(x))

for epoch in range(epochs):
    for xi, target in zip(X, y):
        linear_output = np.dot(xi, weights) + bias
        prediction = sigmoid(linear_output)
        
        error = target - prediction
        
        weights += learning_rate * error * sigmoid_derivative(linear_output) * xi
        bias += learning_rate * error * sigmoid_derivative(linear_output)

print("Trained weights:", weights)
print("Trained bias:", bias)
print("\nTesting NAND gate:")
for xi in X:
    output = sigmoid(np.dot(xi, weights) + bias)
    binary_output = 1 if output >= 0.5 else 0
    print(f"Input: {xi} => Output: {binary_output} (Raw: {output:.4f})")

