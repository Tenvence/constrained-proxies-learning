import torch.utils.data as data
import PIL.Image as Image
import torchvision.transforms as transforms

train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(size=224, scale=(0.08, 1.0), ratio=(3. / 4., 4. / 3.)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4850, 0.4580, 0.4076], std=[0.2290, 0.2240, 0.2250]),
])

eval_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4850, 0.4580, 0.4076], std=[0.2290, 0.2240, 0.2250]),
])


class VisionDataset(data.Dataset):
    def __init__(self, samples, transform):
        super(VisionDataset, self).__init__()
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path)
        img = self.transform(img)
        return img, label


def     get_data_loader(samples, batch_size, is_train, use_ddp=False):
    if is_train:
        dataset = VisionDataset(samples, transform=train_transforms)
        if use_ddp:
            dist_sampler = data.distributed.DistributedSampler(dataset)
            data_loader = data.DataLoader(dataset, batch_size, num_workers=4, sampler=dist_sampler, pin_memory=True, drop_last=True)
        else:
            dist_sampler = None
            data_loader = data.DataLoader(dataset, batch_size, num_workers=4, pin_memory=True, drop_last=True, shuffle=True)
    else:
        dataset = VisionDataset(samples, transform=eval_transforms)
        if use_ddp:
            dist_sampler = data.distributed.DistributedSampler(dataset)
            data_loader = data.DataLoader(dataset, batch_size, num_workers=4, sampler=dist_sampler, pin_memory=True)
        else:
            dist_sampler = None
            data_loader = data.DataLoader(dataset, batch_size, num_workers=4, pin_memory=True)

    return data_loader, dist_sampler