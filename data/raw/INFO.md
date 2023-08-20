## Data provenance
The data in `task.json` is a download (on Aug 19, 2023) of the [understanding_fables](https://github.com/google/BIG-bench/blob/main/bigbench/benchmark_tasks/understanding_fables/task.json) dataset from BIG-bench. 

## Data content and usage
The dataset is a collection of 189 human-written fables of roughly up to ten sentences length together with a human-written moral.
We only use the "examples" field of `task.json`, and from the examples, we only use the "input" (the human-written fable)
as well as the corresponding moral (that key under "target_scores" which maps to 1.)
