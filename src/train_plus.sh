export PYTHONPATH="/root/workspace/arithmetic/ModelTinting/src"
CUDA_VISIBLE_DEVICES=0 python /root/workspace/arithmetic/ModelTinting/src/main_layer_wise_adamerging.py \
    --losstype crosspseudoconf \
    --model ViT-B-32 \
    --prior 0.3 \
    --classifier_train
