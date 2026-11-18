## Step 4: first training launch failed
- NotImplementedError: scaled_dot_product_attention for MPS does not support dropout. Fix: attention_probs_dropout_prob=0.0 (hidden dropout kept). Relaunched.
## Step 5: JPlag hang
- JPlag 6.3.0 spectral clustering threw MaxCountExceededException (convergence failed) on some 150-pair chunks; main thread died but a non-daemon IdleBar thread kept the JVM alive, so the run hung until the 1800 s timeout and the script crashed (TimeoutExpired). Fix: --cluster-skip (clustering does not affect pairwise similarity), 600 s timeout caught; finished chunks reused.
