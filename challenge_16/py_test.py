import torch
import time

# Simple MLP: input -> hidden -> hidden -> output
class SimpleMLP(torch.nn.Module):
    def __init__(self):
        super(SimpleMLP, self).__init__()
        self.fc1 = torch.nn.Linear(100, 128)
        self.fc2 = torch.nn.Linear(128, 128)
        self.fc3 = torch.nn.Linear(128, 10)
        self.relu = torch.nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Generate 100 random input vectors
x = torch.randn(100, 100)

model = SimpleMLP()

start_time = time.time()

# Forward pass
for i in range(1):
    with torch.no_grad():
        output = model(x)

end_time = time.time()

print(f"PyTorch forward time: {(end_time - start_time)*1000:.4f} ms")

