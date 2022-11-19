import time

import sklearn.metrics as metrics
import torch
import torch.cuda.amp as amp


def train(model, criterion, optimizer, lr_scheduler, data_loader):
    model.train()
    scaler = amp.GradScaler()
    losses = []

    st = time.time()
    for img, label in data_loader:
        img = img.cuda(non_blocking=True)
        label = label.cuda(non_blocking=True)

        optimizer.zero_grad()
        with amp.autocast():
            assign_metric, proxies_metric = model(img)
            loss = criterion(assign_metric, label, proxies_metric)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        losses.append(loss.detach())

    if lr_scheduler is not None:
        lr_scheduler.step()

    et = time.time()

    return sum(losses) / len(losses), et - st


@torch.no_grad()
def val(model, data_loader):
    model.eval()
    pred_list, gt_list = [], []

    st = time.time()
    for img, label in data_loader:
        img = img.cuda(non_blocking=True)
        with amp.autocast():
            assign_metric, proxies_metric = model(img)
            pred = torch.argmax(assign_metric, dim=-1)
        pred_list.append(pred)
        gt_list.append(label)
    et = time.time()

    pred_list = torch.cat(pred_list, dim=0).cpu()
    gt_list = torch.cat(gt_list, dim=0)

    acc = metrics.accuracy_score(gt_list, pred_list) * 100
    mae = metrics.mean_absolute_error(gt_list, pred_list)

    acc = torch.tensor(acc).cuda()
    mae = torch.tensor(mae).cuda()

    return acc, mae, et - st
