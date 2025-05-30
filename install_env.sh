# create python env
if conda env list | grep -q "^crawler\s"; then
    echo "环境 'crawler' 已存在，跳过创建"
else
    # 创建python环境
    echo "正在创建环境 'crawler'..."
    conda create -n crawler python==3.13 -y
fi

# activate env
conda activate crawler

# install requirements
pip install -r requirements.txt