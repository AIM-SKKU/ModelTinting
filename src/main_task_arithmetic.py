import os

import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "3"

import time
import sys
sys.path.append('/root/workspace/arithmetic/AdaMerging')

from task_vectors import TaskVector
from eval import eval_single_dataset, eval_single_dataset_with_ece
from args import parse_arguments

def create_log_dir(path, filename='log.txt'):
    import logging
    if not os.path.exists(path):
        os.makedirs(path)
    logger = logging.getLogger(path)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(path+'/'+filename)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

############ 8 tasks ############
exam_datasets = ['SUN397', 'Cars', 'RESISC45', 'EuroSAT', 'SVHN', 'GTSRB', 'MNIST', 'DTD'] # SUN397 | Cars | RESISC45 | EuroSAT | SVHN | GTSRB | MNIST | DTD
###################################


############ 14 tasks ############
# exam_datasets = [
#     "MNIST",
#     "Cars",
#     "DTD",
#     "EuroSAT",
#     "GTSRB",
#     "RESISC45",
#     "SUN397",
#     "SVHN",
#     "PCAM",
#     "CIFAR100",
#     "STL10",
#     "OxfordIIITPet",
#     "Flowers102",
#     "FER2013",
# ]
###################################



############ 20 tasks ############
# exam_datasets = [
#     "MNIST",
#     "Cars",
#     "DTD",
#     "EuroSAT",
#     "GTSRB",
#     "RESISC45",
#     "SUN397",
#     "SVHN",
#     "PCAM",
#     "CIFAR100",
#     "STL10",
#     "OxfordIIITPet",
#     "Flowers102",
#     "FER2013",
#     "CIFAR10",
#     "Food101",
#     "RenderedSST2",
#     "EMNIST",
#     "FashionMNIST",
#     "KMNIST",
# ]
###################################

model = 'ViT-B-32'
args = parse_arguments()
args.data_location = '/root/datasets/multitask'
args.model = model
args.save = '/root/workspace/arithmetic/AdaMerging/checkpoints/' + model
args.logs_path = '/root/workspace/arithmetic/AdaMerging/logs/' + model
pretrained_checkpoint = '/root/workspace/arithmetic/AdaMerging/checkpoints/'+model+'/zeroshot.pt'

str_time_ = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
log = create_log_dir(args.logs_path, 'log_{}_task_arithmetic.txt'.format(str_time_))

task_vectors = [
    TaskVector(pretrained_checkpoint, '/root/workspace/arithmetic/AdaMerging/checkpoints/'+model+'/'+dataset_name+'/finetuned.pt') for dataset_name in exam_datasets
]

task_vector_sum = sum(task_vectors)

scaling_coef_ = 0.3  # 8 tasks
# scaling_coef_ = 1.0
# scaling_coef_ = 0.1 # 20task, 14tasks

scaling_coef_ = 1/(len(exam_datasets)) # weight average



image_encoder = task_vector_sum.apply_to(pretrained_checkpoint, scaling_coef=scaling_coef_)
log.info('*'*20 + 'scaling_coef:' + str(scaling_coef_) + '*'*20)

# accs = []
# for dataset in exam_datasets:
#     metrics = eval_single_dataset(image_encoder, dataset, args)
#     log.info(str(dataset) + ':' + str(metrics.get('top1')*100)+'%')
#     accs.append(metrics.get('top1')*100)
# log.info('Avg ACC:' + str(np.mean(accs)) + '%')




# for ece
accs = []
for dataset in exam_datasets:
    metrics = eval_single_dataset_with_ece(image_encoder, dataset, args)
    log.info(str(dataset) + ':' + str(metrics.get('top1')*100)+'%')
    accs.append(metrics.get('top1')*100)
log.info('Avg ACC:' + str(np.mean(accs)) + '%')


