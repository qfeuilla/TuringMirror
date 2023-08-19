# TuringMirror
A benchmark to test whether AI are able to recognize their own output from human or other AI

## Install

**Poetry (recommended).** This repository utilizes [poetry](https://python-poetry.org/) for package management. Poetry automatically generates and manages a virtual environment for you, and also installs the `turingmirror` module itself. If you have poetry installed, running the following command will install everything you need:

```commandline
poetry install
```

**pip and `requirements.txt`.** Alternatively, `pip` can be used to install dependencies with `pip install -r requirements.txt`.

Please note, when using `pip`, you're responsible for managing any virtual environments and deciding where packages should be installed.

## Dataset
We use the [understanding_fables](https://github.com/google/BIG-bench/blob/main/bigbench/benchmark_tasks/understanding_fables/task.json) dataset from BIG-bench. 
The dataset is a collection of 190 human-written fables of roughly up to ten sentences length together with a human-written moral.

### Generation of AI-written fables
We enrich this dataset of human-written fables with fables written by different AI models (GPT-3.5, GPT-4, Claude2) by prompting the models with the moral and ask it to write a fable of up to around ten sentences length illustrating the moral.

We use JSONLines format for our generated datasets.

## Test
We then test whether the AI models are able to recognize their own output from human-written fables or fables written by different AI models.

We test one-vs-one in the following configurations:

- Human vs other AI
- Human vs AI under test
- AI under test vs other AI

For each of the samples we generate a binary multiple-choice prompt for which we randomize the order to eliminate order-bias.

## Results
...

