import os
os.environ["CUDA_VISIBLE_DEVICES"] = "2"

import time
import sys
sys.path.append('/root/workspace/arithmetic/AdaMerging')

from eval import eval_single_dataset
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

exam_datasets = ['SUN397', 'Cars', 'RESISC45', 'EuroSAT', 'SVHN', 'GTSRB', 'MNIST', 'DTD'] # SUN397 | Cars | RESISC45 | EuroSAT | SVHN | GTSRB | MNIST | DTD
exam_datasets = [
    "MNIST",
    "Cars",
    "DTD",
    "EuroSAT",
    "GTSRB",
    "RESISC45",
    "SUN397",
    "SVHN",
    "PCAM",
    "CIFAR100",
    "STL10",
    "OxfordIIITPet",
    "Flowers102",
    "FER2013",
    "CIFAR10",
    "Food101",
    "RenderedSST2",
    "EMNIST",
    "FashionMNIST",
    "KMNIST",
]

exam_datasets = [
    "MNIST",
    "Cars",
    "DTD",
    "EuroSAT",
    "GTSRB",
    "RESISC45",
    "SUN397",
    "SVHN",
    "PCAM",
    "CIFAR100",
    "STL10",
    "OxfordIIITPet",
    "Flowers102",
    "FER2013",
]

##### task 14, 20
scaling_coef_ = 0.1

# #task 8
# scaling_coef_ = 0.3


model = 'ViT-B-32'
args = parse_arguments()
source_root_path = '/root/workspace/arithmetic/AdaMerging'
args.data_location = '/root/datasets/multitask'
args.model = model
args.save = source_root_path+'/checkpoints/' + model
args.logs_path = '/root/workspace/arithmetic/AdaMerging/logs/' + model
pretrained_checkpoint = source_root_path+'/checkpoints/'+model+'/zeroshot.pt'

str_time_ = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
log = create_log_dir(args.logs_path, 'log_{}_ties_merging.txt'.format(str_time_))

from ties_merging_utils import *
ft_checks = [torch.load(source_root_path+'/checkpoints/'+model+'/'+dataset_name+'/finetuned.pt').state_dict() for dataset_name in exam_datasets]
ptm_check = torch.load(pretrained_checkpoint).state_dict()
check_parameterNamesMatch(ft_checks + [ptm_check])

remove_keys = []
print(f"Flattening out Checkpoints")
flat_ft = torch.vstack([state_dict_to_vector(check, remove_keys) for check in ft_checks])
flat_ptm = state_dict_to_vector(ptm_check, remove_keys)

tv_flat_checks = flat_ft - flat_ptm
assert check_state_dicts_equal(vector_to_state_dict(flat_ptm, ptm_check, remove_keys), ptm_check)
assert all([check_state_dicts_equal(vector_to_state_dict(flat_ft[i], ptm_check, remove_keys), ft_checks[i])for i in range(len(ft_checks))])


K = 20
merge_func = "dis-sum"




merged_tv = ties_merging(tv_flat_checks, reset_thresh=K, merge_func=merge_func,)
merged_check = flat_ptm + scaling_coef_ * merged_tv
merged_state_dict = vector_to_state_dict(merged_check, ptm_check, remove_keys=remove_keys)

image_encoder = torch.load(pretrained_checkpoint)
image_encoder.load_state_dict(merged_state_dict, strict=False)

Total_ACC = 0.
for dataset in exam_datasets:
    metrics = eval_single_dataset(image_encoder, dataset, args)
    Total_ACC += metrics['top1']
    log.info(str(dataset) + ':' + str(metrics))

log.info('Final: ' + 'Avg ACC:' + str(Total_ACC / len(exam_datasets)))
