# comma.ai Controls Challenge 

> **Final Score: 95.16** | Baseline PID: 110.25 

## The Problem

comma.ai recorded thousands of real people driving on real roads.
Given that data, can you write a controller that steers a simulated 
car along the same path — smoothly and accurately?

Two things are measured:
- **lataccel_cost** — how far off the target path you are (weighted ×50)
- **jerk_cost** — how jerky/rough your steering is
- **total_cost = (lataccel_cost × 50) + jerk_cost** → lower is better

## My Insight

The baseline PID only looks at **right now** — current position vs target.
It never sees what's coming.

I added a single **feedforward term** using `future_plan.lataccel[0]` — 
a one-step lookahead into where the road is going next.

Think of the difference between:
- A driver who **reacts** to drifting after it happens
- A driver who **sees the curve coming** and steers early



## The Controller
```python
pid = p * error + i * error_integral + d * error_diff
ff  = future_plan.lataccel[0]
return pid + 0.34 * ff
```

## Tuning Process

I tuned systematically — one variable at a time, observing both 
lataccel_cost and jerk_cost separately at each step.

**Phase 1 — Find the right feedforward weight:**

| FF weight | Score (5 segs) | Notes |
|---|---|---|
| 0.00 | 67.3 | Baseline PID, no lookahead |
| 0.05 | 63.85 | First improvement |
| 0.15 | 58.14 | Getting better |
| 0.30 | 55.36 | Good |
| 0.34 | 54.59 | Sweet spot ✅ |
| 0.36 | 55.44 | Jerk starts increasing |
| 0.50 | 61.17 | Too aggressive, overshoots |

**Phase 2 — Fine tune PID gains to reduce jerk on 5000 segments:**

| p | i | d | Score (5000 segs) |
|---|---|---|---|
| 0.195 | 0.100 | -0.053 | 101.1 (original gains) |
| 0.190 | 0.095 | -0.060 | **95.16** ✅ |

## Key Learnings

- The **feedforward term is the biggest lever** — reacting early beats reacting fast
- `lataccel_cost × 50` means path accuracy matters far more than smoothness
- Tuning gains on 5 segments first (fast) then validating on 5000 (slow) saves time
- The baseline PID's **negative D gain** (-0.053) is intentional — it actively damps oscillation

## Results
```
Average lataccel_cost:  1.305
Average jerk_cost:     29.94
Average total_cost:    95.16  
```

## How to Run
```bash
# Setup
git clone https://github.com/priyanka-bh2/controls_challenge
cd controls_challenge
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run my controller
python tinyphysics.py --model_path ./models/tinyphysics.onnx \
  --data_path ./data --num_segs 5000 --controller priyanka

# Compare against baseline
python eval.py --model_path ./models/tinyphysics.onnx \
  --data_path ./data --num_segs 5000 \
  --test_controller priyanka --baseline_controller pid
```


