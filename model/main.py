import argparse
from model import *
parser = argparse.ArgumentParser()

def train():
    ### Parse arguments here ###
    ts_dir = '../data/timeseries_data'
    vec_dir = '../data/news_vectors'
    kg_dir = '../saved_embeddings'
    parameters = {'seq_len': 5, 'lr': 0.0005, 'epochs': 50}
    ### Parse arguments here ###

    lstm = LSTM(
        ts_dir = ts_dir,
        vec_dir = vec_dir,
        kg_dir = kg_dir,
        parameters=parameters
    )
    lstm.train()


def train_kg(root,model,combine):
    ### Parse arguments here ###
    ts_dir = root + 'data/timeseries_data/'
    kg_dir = root + 'data/news_vectors/'
    parameters = {'seq_len': 5, 'lr': 0.0005, 'epochs': 50, 'kg_size':8, 'hidden_size':20}
    ### Parse arguments here ###

    lstm = LSTM_KG(
        ts_dir = ts_dir,
        kg_dir = kg_dir,
        parameters=parameters,
        model=model,
        combine=combine
    )
    lstm.train()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, choices=['TransE','TransD'], default='TransE',help="TransE or TransD")
    parser.add_argument("--combine",type=bool,default=False, help="combine feature or kg feature")
    parser.add_argument("--root",type=str, default= '../',help="root path")
    args = parser.parse_args()
    for i in range(5):
        train_kg(root=args.root,model=args.model,combine=args.combine)
        train()
