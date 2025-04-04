import torch
import torch.nn as nn
import numpy as np
import torch.nn.functional as F
from einops import rearrange

def attention(query, key, value):
    """Advanced attention mechanism for neural feature integration"""
    dim = query.size(-1)
    scores = torch.einsum('bhqd,bhkd->bhqk', query, key) / dim**.5
    attn = F.softmax(scores, dim=-1)
    out = torch.einsum('bhqk,bhkd->bhqd', attn, value)
    return out, attn

class EnhancedVariancePooling(nn.Module):
    """Advanced variance-based pooling with logarithmic normalization"""
    def __init__(self, kernel_size, stride):
        super().__init__()
        self.kernel_size = kernel_size
        self.stride = stride
    
    def forward(self, x):
        t = x.shape[2]
        out_shape = (t - self.kernel_size) // self.stride + 1
        out = []

        for i in range(out_shape):
            index = i*self.stride
            input = x[:, :, index:index+self.kernel_size]
            # Enhanced variance calculation with improved numerical stability
            output = torch.log(torch.clamp(input.var(dim=-1, keepdim=True), 1e-6, 1e6))
            out.append(output)

        out = torch.cat(out, dim=-1)
        return out

class AdvancedMultiHeadAttention(nn.Module):
    """Multi-head attention with improved feature projection"""
    def __init__(self, d_model, n_head, dropout):
        super().__init__()
        self.d_k = d_model // n_head
        self.d_v = d_model // n_head
        self.n_head = n_head

        # Enhanced projection matrices
        self.w_q = nn.Linear(d_model, n_head*self.d_k)
        self.w_k = nn.Linear(d_model, n_head*self.d_k)
        self.w_v = nn.Linear(d_model, n_head*self.d_v)
        self.w_o = nn.Linear(n_head*self.d_v, d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(self, query, key, value):
        # Advanced tensor reshaping for multi-head processing
        q = rearrange(self.w_q(query), "b n (h d) -> b h n d", h=self.n_head)
        k = rearrange(self.w_k(key), "b n (h d) -> b h n d", h=self.n_head)
        v = rearrange(self.w_v(value), "b n (h d) -> b h n d", h=self.n_head)
        
        out, _ = attention(q, k, v)
        
        out = rearrange(out, 'b h q d -> b q (h d)')
        out = self.dropout(self.w_o(out))

        return out

class AdvancedFeedForward(nn.Module):
    """Enhanced feed-forward network with GELU activation"""
    def __init__(self, d_model, d_hidden, dropout):
        super().__init__()
        self.w_1 = nn.Linear(d_model, d_hidden)
        # Using GELU for improved gradient flow
        self.act = nn.GELU()
        self.w_2 = nn.Linear(d_hidden, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # Two-stage processing with regularization
        x = self.w_1(x)
        x = self.act(x)
        x = self.dropout(x)
        x = self.w_2(x)
        x = self.dropout(x)

        return x

class EnhancedTransformerBlock(nn.Module):
    """Advanced transformer block with pre-normalization architecture"""
    def __init__(self, embed_dim, num_heads, fc_ratio, attn_drop=0.5, fc_drop=0.5):
        super().__init__()
        self.multihead_attention = AdvancedMultiHeadAttention(embed_dim, num_heads, attn_drop)
        self.feed_forward = AdvancedFeedForward(embed_dim, embed_dim*fc_ratio, fc_drop)
        # Using layer normalization for improved training stability
        self.layernorm1 = nn.LayerNorm(embed_dim)
        self.layernorm2 = nn.LayerNorm(embed_dim)
    
    def forward(self, data):
        # Pre-normalization architecture for improved gradient flow
        res = self.layernorm1(data)
        out = data + self.multihead_attention(res, res, res)

        res = self.layernorm2(out)
        output = out + self.feed_forward(res)
        return output

class NeuroTransNet(nn.Module):
    """
    Advanced EEG analysis model with multi-scale temporal processing,
    dual-path feature extraction, and transformer-based integration.
    
    This model employs a novel architecture specifically designed for
    EEG signal processing with enhanced feature extraction capabilities.
    """
    def __init__(self, num_classes=4, num_samples=1000, num_channels=22, embed_dim=32, pool_size=50, 
    pool_stride=15, num_heads=8, fc_ratio=4, depth=4, attn_drop=0.5, fc_drop=0.5):
        super().__init__()
        # Multi-scale temporal convolutions for comprehensive feature extraction
        self.temporal_conv_small = nn.Conv2d(1, embed_dim//4, (1, 15), padding=(0, 7))
        self.temporal_conv_medium = nn.Conv2d(1, embed_dim//4, (1, 25), padding=(0, 12))
        self.temporal_conv_large = nn.Conv2d(1, embed_dim//4, (1, 51), padding=(0, 25))
        self.temporal_conv_xlarge = nn.Conv2d(1, embed_dim//4, (1, 65), padding=(0, 32))
        
        # Normalization for improved training stability
        self.batch_norm1 = nn.BatchNorm2d(embed_dim)
        
        # Spatial feature extraction
        self.spatial_conv = nn.Conv2d(embed_dim, embed_dim, (num_channels, 1))
        self.batch_norm2 = nn.BatchNorm2d(embed_dim)
        self.activation = nn.ELU()

        # Dual-path feature pooling
        self.variance_pooling = EnhancedVariancePooling(pool_size, pool_stride)
        self.average_pooling = nn.AvgPool1d(pool_size, pool_stride)

        # Calculate embedding dimension
        self.temporal_embedding_dim = (num_samples - pool_size) // pool_stride + 1

        # Regularization
        self.dropout = nn.Dropout()

        # Transformer-based feature integration
        self.transformer_blocks = nn.ModuleList(
            [EnhancedTransformerBlock(embed_dim, num_heads, fc_ratio, attn_drop, fc_drop) for i in range(depth)]
        )

        # Feature encoding and classification
        self.feature_encoder = nn.Sequential(
            nn.Conv2d(122, 64, (2, 1)),
            nn.BatchNorm2d(64),
            nn.ELU()
        )
        
        # Final classification layer
        self.classifier = nn.Linear(embed_dim*self.temporal_embedding_dim, num_classes)
        
        # Initialize weights for optimal convergence
    #     self._initialize_weights()
    
    # def _initialize_weights(self):
    #     """Advanced weight initialization for improved convergence"""
    #     for m in self.modules():
    #         if isinstance(m, nn.Conv2d):
    #             nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
    #             if m.bias is not None:
    #                 nn.init.constant_(m.bias, 0)
    #         elif isinstance(m, nn.BatchNorm2d):
    #             nn.init.constant_(m.weight, 1)
    #             nn.init.constant_(m.bias, 0)
    #         elif isinstance(m, nn.Linear):
    #             nn.init.xavier_normal_(m.weight)
    #             nn.init.constant_(m.bias, 0)

    def forward(self, x):
        # Input preparation
        x = x.unsqueeze(dim=1)  # [batch, 1, channels, samples]
        
        # Multi-scale temporal feature extraction
        x1 = self.temporal_conv_small(x)
        x2 = self.temporal_conv_medium(x)
        x3 = self.temporal_conv_large(x)
        x4 = self.temporal_conv_xlarge(x)
        
        # Feature fusion
        x = torch.cat((x1, x2, x3, x4), dim=1)
        x = self.batch_norm1(x)

        # Spatial feature extraction
        x = self.spatial_conv(x)
        x = self.batch_norm2(x)
        x = self.activation(x)
        x = x.squeeze(dim=2)  # [batch, embed_dim, samples]

        # Dual-path feature pooling
        x1 = self.average_pooling(x)  # Mean statistics
        x2 = self.variance_pooling(x)  # Variance statistics

        # Regularization
        x1 = self.dropout(x1)
        x2 = self.dropout(x2)

        # Prepare for transformer processing
        x1 = rearrange(x1, 'b d n -> b n d')  # [batch, seq_len, features]
        x2 = rearrange(x2, 'b d n -> b n d')

        # Apply transformer blocks for feature integration
        for transformer in self.transformer_blocks:
            x1 = transformer(x1)
            x2 = transformer(x2)
        
        # Prepare for feature encoding
        x1 = x1.unsqueeze(dim=2)
        x2 = x2.unsqueeze(dim=2)

        # Feature fusion
        x = torch.cat((x1, x2), dim=2)
        x = self.feature_encoder(x)

        # Final classification
        x = x.reshape(x.size(0), -1)
        out = self.classifier(x)

        return out
