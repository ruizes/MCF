import torch
import numpy as np
from tqdm import tqdm
from torch.utils.data import DataLoader
from utils.losses import entropy_loss

class ActiveLearner:
    def __init__(self, model, query_strategy='entropy', num_query=10):
        self.model = model
        self.query_strategy = query_strategy
        self.num_query = num_query
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
    def query(self, unlabeled_loader):
        """
        Query the most informative samples from unlabeled data
        """
        self.model.eval()
        scores = []
        
        with torch.no_grad():
            for batch in tqdm(unlabeled_loader, desc='Querying samples'):
                inputs = batch['image'].to(self.device)
                outputs = self.model(inputs)
                outputs_soft = torch.softmax(outputs, dim=1)
                
                if self.query_strategy == 'entropy':
                    score = entropy_loss(outputs_soft)
                elif self.query_strategy == 'least_confidence':
                    score = 1 - torch.max(outputs_soft, dim=1)[0].mean()
                elif self.query_strategy == 'margin':
                    sorted_probs, _ = torch.sort(outputs_soft, dim=1, descending=True)
                    score = 1 - (sorted_probs[:, 0] - sorted_probs[:, 1]).mean()
                else:
                    raise ValueError(f'Unknown query strategy: {self.query_strategy}')
                    
                scores.append(score.item())
        
        # Get indices of top N samples with highest scores
        indices = np.argsort(scores)[-self.num_query:]
        return indices
    
    def update_labeled_set(self, labeled_set, unlabeled_set, selected_indices):
        """
        Update labeled set by moving selected samples from unlabeled set
        """
        selected_samples = [unlabeled_set[i] for i in selected_indices]
        labeled_set.extend(selected_samples)
        
        # Remove selected samples from unlabeled set
        unlabeled_set = [unlabeled_set[i] for i in range(len(unlabeled_set)) if i not in selected_indices]
        
        return labeled_set, unlabeled_set
