import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
from dataloader import TrainSet
import math
from gensim.models import KeyedVectors
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class TranE(nn.Module):
    def __init__(self, device, word_dim=300, d_norm=2, gamma=1,model_path = '../data/GoogleNews-vectors-negative300.bin'):
        """
        :param entity_num: number of entities
        :param relation_num: number of relations
        :param dim: embedding dim
        :param device:
        :param d_norm: measure d(h+l, t), either L1-norm or L2-norm
        :param gamma: margin hyperparameter
        """
        super(TranE, self).__init__()
        self.word_dim = word_dim
        self.d_norm = d_norm
        self.device = device
        self.gamma = torch.FloatTensor([gamma]).to(self.device)
        self.head_mapping = nn.Parameter(torch.FloatTensor(word_dim,word_dim))
        self.model = KeyedVectors.load_word2vec_format(model_path, binary=True)
        self.tail_mapping = nn.Parameter(torch.FloatTensor(word_dim,word_dim))
        # l <= l / ||l||
        #relation_norm = torch.norm(self.relation_embedding.weight.data, dim=1, keepdim=True)
        self.reset_parameters()
    
    def reset_parameters(self):
        nn.init.xavier_uniform_(self.head_mapping)
        nn.init.xavier_uniform_(self.tail_mapping)

    def word2vec(self, txt):
        # Remove punctuation
        #print('before process:',txt)
        #txt = txt.translate(str.maketrans('', '', string.punctuation))
        # Remove exception terms

        #resultwords  = [word for word in txt.split() if word in self.model]
        #txt = ' '.join(resultwords)
        #vec = []  
        #print('after:',txt)


      # Tokenize the string into words
        tokens = word_tokenize(txt)
       # Remove non-alphabetic tokens, such as punctuation
        words = [word.lower() for word in tokens if word.isalpha()]
       # Filter out stopwords
        #stop_words = set(stopwords.words('english'))
        #words = [word for word in words if not word in stop_words]
        #print(words)
        vector_list = [self.model[word] for word in words if word in self.model]
        if len(vector_list) == 0:
            #print('None')
            return None
        return torch.Tensor(np.mean(np.array(vector_list), axis=0)).unsqueeze(0)

    def calculate_loss(self, pos_dis, neg_dis):
        """
        :param pos_dis: [batch_size, embed_dim]
        :param neg_dis: [batch_size, embed_dim]
        :return: triples loss: [batch_size]
        """
        distance_diff = self.gamma + torch.norm(pos_dis, p=self.d_norm, dim=1) - torch.norm(neg_dis, p=self.d_norm,dim=1)
        return torch.sum(F.relu(distance_diff))

    def forward(self, pos_head, pos_relation, pos_tail, neg_head, neg_relation, neg_tail):
        """
        :param pos_head: [batch_size]
        :param pos_relation: [batch_size]
        :param pos_tail: [batch_size]
        :param neg_head: [batch_size]
        :param neg_relation: [batch_size]
        :param neg_tail: [batch_size]
        :return: triples loss
        """
        pos_dis = torch.mm(pos_head,self.head_mapping) + pos_relation - torch.mm(pos_tail,self.tail_mapping)
        neg_dis = torch.mm(neg_head,self.head_mapping) + neg_relation - torch.mm(neg_tail,self.tail_mapping)
        # return pos_head_and_relation, pos_tail, neg_head_and_relation, neg_tail
        return self.calculate_loss(pos_dis, neg_dis).requires_grad_()

    def predict(self, head, relation, tail):
        return torch.cat((torch.mm(head,self.head_mapping).squeeze(),relation.squeeze(),torch.mm(tail,self.tail_mapping).squeeze()))

class TranD(nn.Module):
    def __init__(self, device, word_dim=300, d_norm=2, gamma=1,model_path = '../data/GoogleNews-vectors-negative300.bin'):
        """
        :param entity_num: number of entities
        :param relation_num: number of relations
        :param dim: embedding dim
        :param device:
        :param d_norm: measure d(h+l, t), either L1-norm or L2-norm
        :param gamma: margin hyperparameter
        """
        super(TranD, self).__init__()
        self.word_dim = word_dim
        self.d_norm = d_norm
        self.device = device
        self.gamma = torch.FloatTensor([gamma]).to(self.device)
        self.head_mapping = nn.Parameter(torch.FloatTensor(1,word_dim))
        self.model = KeyedVectors.load_word2vec_format(model_path, binary=True)
        self.tail_mapping = nn.Parameter(torch.FloatTensor(1,word_dim))
        self.relation_mapping = nn.Parameter(torch.FloatTensor(word_dim,1))
        self.I = torch.eye(word_dim)
        #self.triple_num = 

        # l <= l / ||l||
        #relation_norm = torch.norm(self.relation_embedding.weight.data, dim=1, keepdim=True)
        self.reset_parameters()
    
    def reset_parameters(self):
        nn.init.xavier_uniform_(self.head_mapping)
        nn.init.xavier_uniform_(self.tail_mapping)
        nn.init.xavier_uniform_(self.relation_mapping)

    def word2vec(self, txt):
        # Remove punctuation
        #print('before process:',txt)
        #txt = txt.translate(str.maketrans('', '', string.punctuation))
        # Remove exception terms

        #resultwords  = [word for word in txt.split() if word in self.model]
        #txt = ' '.join(resultwords)
        #vec = []  
        #print('after:',txt)


      # Tokenize the string into words
        tokens = word_tokenize(txt)
       # Remove non-alphabetic tokens, such as punctuation
        words = [word.lower() for word in tokens if word.isalpha()]
       # Filter out stopwords
        #stop_words = set(stopwords.words('english'))
        #words = [word for word in words if not word in stop_words]
        #print(words)
        vector_list = [self.model[word] for word in words if word in self.model]
        if len(vector_list) == 0:
            #print('None')
            return None
        return torch.Tensor(np.mean(np.array(vector_list), axis=0)).unsqueeze(0)

    def calculate_loss(self, pos_dis, neg_dis):
        """
        :param pos_dis: [batch_size, embed_dim]
        :param neg_dis: [batch_size, embed_dim]
        :return: triples loss: [batch_size]
        """
        distance_diff = self.gamma + torch.norm(pos_dis, p=self.d_norm, dim=1) - torch.norm(neg_dis, p=self.d_norm,dim=1)
        return torch.sum(F.relu(distance_diff))

    def forward(self, pos_head, pos_relation, pos_tail, neg_head, neg_relation, neg_tail):
        """
        :param pos_head: [batch_size]
        :param pos_relation: [batch_size]
        :param pos_tail: [batch_size]
        :param neg_head: [batch_size]
        :param neg_relation: [batch_size]
        :param neg_tail: [batch_size]
        :return: triples loss
        """
        M_rh = torch.mm(self.relation_mapping,self.head_mapping)+self.I
        M_rt = torch.mm(self.relation_mapping,self.tail_mapping)+self.I
        pos_dis = torch.mm(pos_head,M_rh) + pos_relation - torch.mm(pos_tail,M_rt)
        neg_dis = torch.mm(neg_head,M_rh) + neg_relation - torch.mm(neg_tail,M_rt)
        # return pos_head_and_relation, pos_tail, neg_head_and_relation, neg_tail
        return self.calculate_loss(pos_dis, neg_dis).requires_grad_()

    def predict(self, head, relation, tail):
        M_rh = torch.mm(self.relation_mapping,self.head_mapping)+self.I
        M_rt = torch.mm(self.relation_mapping,self.tail_mapping)+self.I
        return torch.cat((torch.mm(head,M_rh).squeeze(),relation.squeeze(),torch.mm(tail,M_rt).squeeze()))
   
if __name__ == '__main__':
    train_data_set = TrainSet()
    train_loader = DataLoader(train_data_set, batch_size=32, shuffle=True)
    for batch_idx, data in enumerate(train_loader):
        print(data.shape)
        break