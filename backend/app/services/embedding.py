import os
import numpy as np
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer
import onnxruntime as ort

MODEL_ID = "Xenova/all-MiniLM-L6-v2"

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super(EmbeddingService, cls).__new__(cls)
            instance._initialize()
            cls._instance = instance
        return cls._instance

    def _initialize(self):
        # Securely download or get cached INT8 ONNX model + Tokenizer
        tokenizer_path = hf_hub_download(repo_id=MODEL_ID, filename="tokenizer.json")
        model_path = hf_hub_download(repo_id=MODEL_ID, filename="onnx/model_quantized.onnx")

        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        # The rust tokenizer truncates by default if configured, but we can enforce it
        # self.tokenizer.enable_truncation(max_length=512)
        
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

    def get_embedding(self, text: str) -> np.ndarray:
        # Tokenize
        encoding = self.tokenizer.encode(text)
        
        # Inputs expected by BERT-like models
        input_ids = np.array([encoding.ids], dtype=np.int64)
        attention_mask = np.array([encoding.attention_mask], dtype=np.int64)
        
        # Xenova MiniLM also expects token_type_ids
        token_type_ids = np.array([encoding.type_ids], dtype=np.int64)
        
        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids
        }
        
        outputs = self.session.run(None, inputs)
        
        # Mean Pooling
        last_hidden_state = outputs[0]
        mask_expanded = np.expand_dims(attention_mask, -1)
        sum_embeddings = np.sum(last_hidden_state * mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
        
        sentence_embedding = sum_embeddings / sum_mask
        
        # L2 Normalization
        norm = np.linalg.norm(sentence_embedding, axis=1, keepdims=True)
        normalized_embedding = sentence_embedding / np.clip(norm, a_min=1e-9, a_max=None)
        
        return normalized_embedding[0]

# Global singleton instance provider
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
