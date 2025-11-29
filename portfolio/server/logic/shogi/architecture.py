import torch
import torch.nn as nn
import torch.nn.functional as F

class ShogiCNN(nn.Module):
    def __init__(self):
        super(ShogiCNN, self).__init__()

        # 畳み込み層
        self.conv1 = nn.Conv2d(in_channels=40, out_channels=128, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(in_channels=256, out_channels=512, kernel_size=3, padding=1)

        # 全結合層
        self.fc1 = nn.Linear(512 * 9 * 9, 1024)
        self.fc2 = nn.Linear(1024, 6561)  # 出力: 6561クラス (from + to)

    def forward(self, x):
        # CNN部分
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))

        # Flatten
        x = x.view(x.size(0), -1)

        # Fully connected
        x = F.relu(self.fc1(x))
        x = self.fc2(x)

        return x

model = ShogiCNN()
sample_input = torch.randn(4, 40, 9, 9)  # batch_size = 4
output = model(sample_input)

print(output.shape)  # torch.Size([4, 6561])
