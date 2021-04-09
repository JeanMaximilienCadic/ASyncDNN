import argparse
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
import torch
from sakura.ml import AsyncTrainer
from sakura import defaultMetrics
from .trainer import Trainer
from .model import Net

if __name__ == "__main__":
    # Training settings
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--batch-size', type=int, default=640, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',
                        help='input batch size for testing (default: 1000)')
    parser.add_argument('--epochs', type=int, default=10, metavar='N',
                        help='number of epochs to train (default: 14)')
    parser.add_argument('--lr', type=float, default=1.0, metavar='LR',
                        help='learning rate (default: 1.0)')
    parser.add_argument('--gamma', type=float, default=0.7, metavar='M',
                        help='Learning rate step gamma (default: 0.7)')
    parser.add_argument('--no-cuda', action='store_true', default=False,
                        help='disables CUDA training')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='quickly check a single pass')
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')
    parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                        help='how many batches to wait before logging training status')
    parser.add_argument('--save-model', action='store_true', default=False,
                        help='For Saving the current Model')
    args = parser.parse_args()


    # Instantiate
    torch.manual_seed(args.seed)
    use_cuda = "cuda" # use_cuda = not args.no_cuda and torch.cuda.is_available()
    # device = torch.device("cuda" if use_cuda else "cpu")
    train_kwargs = {'batch_size': args.batch_size}
    test_kwargs = {'batch_size': args.test_batch_size}
    if use_cuda:
        cuda_kwargs = {'num_workers': 1,
                       'pin_memory': True,
                       'shuffle': True}
        train_kwargs.update(cuda_kwargs)

    transform=transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
    dataset1, dataset2 = datasets.MNIST('data',
                                        train=False,
                                        download=True,
                                        transform=transform), \
                         datasets.MNIST('data',
                                        train=False,
                                        transform=transform)
    train_loader, test_loader = torch.utils.data.DataLoader(dataset1,**train_kwargs), \
                                torch.utils.data.DataLoader(dataset2, **test_kwargs)
    epochs = args.epochs
    # Instantiate
    model = Net()
    optimizer = optim.Adadelta(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)

    trainer = Trainer(model,
                      optimizer,
                      scheduler,
                      defaultMetrics,
                      epochs,
                      "../mnist_cnn.pt",
                      "mnist_cnn.ckpt.pt",
                      "cuda")

    trainer = AsyncTrainer(trainer)

    trainer.run(train_loader, test_loader)
