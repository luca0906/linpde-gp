# LinPDE-GP: Linear PDE Solvers based on GP Regression

## Getting Started

### Cloning the Repository

This repository includes Git submodules, so it is best cloned via

```shell
git clone --recurse-submodules git@github.com:marvinpfoertner/linpde-gp.git
```

If you forgot the `--recurse-submodules` flag when cloning, simply run

```shell
git submodule update --init --recursive
```

inside the repository.

### Installing a Full Development Environment

```shell
cd path/to/linpde-gp
pip install -r dev-requirements.txt
```

### Interactive Visualizations

In order to run the interactive visualizations in the notebooks with `nb_conda_kernels`,
one needs to install **exactly the same versions** of `ipywidgets` and `ipympl` in the environment running `jupyter` and in the environment of the kernel.
Currently, this works only for `ipympl<=0.7.0`.
