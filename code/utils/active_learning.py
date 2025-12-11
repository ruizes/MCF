import torch
import numpy as np
from torch.utils.data import DataLoader
from tqdm import tqdm

class ActiveLearner:
    def __init__(self, model, query_strategy='entropy'):
        self.model = model
        self.query_strategy = query_strategy
        self.model.eval()
    
    def query(self, unlabeled_loader, num_query=10):
        """
        Query the most informative samples from the unlabeled pool
        Args:
            unlabeled_loader: DataLoader for unlabeled samples
            num_query: Number of samples to query
        Returns:
            selected_indices: Indices of the most informative samples
        """
        if self.query_strategy == 'entropy':
            return self._query_entropy(unlabeled_loader, num_query)
        elif self.query_strategy == 'margin':
            return self._query_margin(unlabeled_loader, num_query)
        elif self.query_strategy == 'least_confidence':
            return self._query_least_confidence(unlabeled_loader, num_query)
        else:
            raise ValueError(f"Unknown query strategy: {self.query_strategy}")
    
    def _query_entropy(self, unlabeled_loader, num_query):
        """
        Query samples with highest entropy
        """
        entropies = []
        with torch.no_grad():
            for batch in tqdm(unlabeled_loader, desc="Calculating entropy"):
                inputs = batch['image'].cuda()
                outputs = self.model(inputs)
                probs = torch.softmax(outputs, dim=1)
                entropy = -torch.sum(probs * torch.log(probs + 1e-6), dim=1)
                entropies.extend(entropy.cpu().numpy())
        
        entropies = np.array(entropies)
        selected_indices = np.argsort(entropies)[::-1][:num_query]
        return selected_indices
    
    def _query_margin(self, unlabeled_loader, num_query):
        """
        Query samples with smallest margin between top two probabilities
        """
        margins = []
        with torch.no_grad():
            for batch in tqdm(unlabeled_loader, desc="Calculating margins"):
                inputs = batch['image'].cuda()
                outputs = self.model(inputs)
                probs = torch.softmax(outputs, dim=1)
                top2_probs = torch.topk(probs, 2, dim=1)[0]
                margin = top2_probs[:, 0] - top2_probs[:, 1]
                margins.extend(margin.cpu().numpy())
        
        margins = np.array(margins)
        selected_indices = np.argsort(margins)[:num_query]
        return selected_indices
    
    def _query_least_confidence(self, unlabeled_loader, num_query):
        """
        Query samples with least confidence in their predictions
        """
        confidences = []
        with torch.no_grad():
            for batch in tqdm(unlabeled_loader, desc="Calculating confidences"):
                inputs = batch['image'].cuda()
                outputs = self.model(inputs)
                probs = torch.softmax(outputs, dim=1)
                confidence = torch.max(probs, dim=1)[0]
                confidences.extend(confidence.cpu().numpy())
        
        confidences = np.array(confidences)
        selected_indices = np.argsort(confidences)[:num_query]
        return selected_indices