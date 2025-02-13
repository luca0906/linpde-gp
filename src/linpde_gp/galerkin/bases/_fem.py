from collections.abc import Sequence
from typing import Union

import numpy as np
import probnum as pn
import scipy.interpolate

from linpde_gp import domains, randprocs
from linpde_gp.problems.pde import DirichletBoundaryCondition
from linpde_gp.typing import DomainLike

from . import _basis


class ZeroBoundaryFiniteElementBasis(_basis.Basis):
    def __init__(
        self,
        domain: DomainLike,
        num_elements: int,
    ):
        super().__init__(size=num_elements)

        self._domain = domains.asdomain(domain)
        self._grid = np.linspace(*self._domain, len(self) + 2)

        # TODO: Implement this as a `LinearOperator`
        self._observation_operator_fn = scipy.interpolate.interp1d(
            x=self._grid,
            y=np.eye(len(self) + 2, len(self), k=-1),
            kind="linear",
            axis=0,
            bounds_error=False,
            fill_value=0.0,
            assume_sorted=True,
        )

    @property
    def grid(self) -> np.ndarray:
        return self._grid

    def __getitem__(self, idx: int) -> pn.functions.Function:
        assert -len(self) <= idx < len(self)

        if idx < 0:
            idx += len(self)

        return pn.functions.LambdaFunction(
            scipy.interpolate.interp1d(
                x=self._grid[idx : idx + 3],
                y=np.array((0.0, 1.0, 0.0)),
                kind="linear",
                bounds_error=False,
                fill_value=0.0,
                assume_sorted=True,
            ),
            input_shape=(),
            output_shape=(),
        )

    def coords2fn(
        self,
        coords: Union[np.ndarray, pn.randvars.RandomVariable],
    ) -> Union[pn.functions.Function, pn.randprocs.RandomProcess]:
        if isinstance(coords, np.ndarray):
            return pn.functions.LambdaFunction(
                scipy.interpolate.interp1d(
                    x=self._grid,
                    y=np.hstack((0.0, coords, 0.0)),
                    kind="linear",
                    bounds_error=False,
                    fill_value=0.0,
                    assume_sorted=True,
                ),
                input_shape=(),
                output_shape=(),
            )

        # Interpret as random variable
        coords = pn.randvars.asrandvar(coords)

        if isinstance(coords, pn.randvars.Constant):
            return randprocs.DeterministicProcess(self.coords2fn(coords.support))

        if isinstance(coords, pn.randvars.Normal):
            return randprocs.ParametricGaussianProcess(
                weights=coords,
                feature_fn=pn.functions.LambdaFunction(
                    self._observation_operator_fn,
                    input_shape=(),
                    output_shape=coords.shape,
                ),
                mean=self.coords2fn(coords.mean),
            )

        raise TypeError("Unsupported type of random variable for argument `coords`")

    def observation_operator(self, xs: np.ndarray) -> np.ndarray:
        return self._observation_operator_fn(xs)


class FiniteElementBasis(_basis.Basis):
    def __init__(
        self,
        domain: DomainLike,
        boundary_conditions: Sequence[DirichletBoundaryCondition],
        num_elements: int,
    ):
        super().__init__(size=num_elements + 2)

        self._domain = domains.asdomain(domain)
        self._boundary_conditions = boundary_conditions

        self._grid = np.linspace(*self._domain, len(self))

        # TODO: Implement this as a `LinearOperator`
        self._observation_operator_fn = scipy.interpolate.interp1d(
            x=self._grid,
            y=np.eye(len(self)),
            kind="linear",
            axis=0,
            bounds_error=False,
            fill_value=0.0,
            assume_sorted=True,
        )

    @property
    def grid(self) -> np.ndarray:
        return self._grid

    def __getitem__(self, idx: int) -> pn.functions.Function:
        assert -len(self) <= idx < len(self)

        if idx < 0:
            idx += len(self)

        xs = self._grid[max(idx - 1, 0) : min(idx + 2, len(self))]

        if idx == 0:
            ys = (1.0, 0.0)
        elif idx == len(self) - 1:
            ys = (0.0, 1.0)
        else:
            ys = (0.0, 1.0, 0.0)

        ys = np.array(ys)

        return pn.functions.LambdaFunction(
            lambda x: np.interp(x, xs, ys),
            input_shape=(),
            output_shape=(),
        )

    def coords2fn(
        self,
        coords: Union[np.ndarray, pn.randvars.RandomVariable],
    ) -> Union[pn.functions.Function, pn.randprocs.RandomProcess]:
        if isinstance(coords, np.ndarray):
            return pn.functions.LambdaFunction(
                scipy.interpolate.interp1d(
                    x=self._grid,
                    y=coords,
                    kind="linear",
                    bounds_error=False,
                    fill_value=0.0,
                    assume_sorted=True,
                ),
                input_shape=(),
                output_shape=(),
            )

        # Interpret as random variable
        coords = pn.randvars.asrandvar(coords)

        if isinstance(coords, pn.randvars.Constant):
            return randprocs.DeterministicProcess(self.coords2fn(coords.support))

        if isinstance(coords, pn.randvars.Normal):
            return randprocs.ParametricGaussianProcess(
                weights=coords,
                feature_fn=pn.functions.LambdaFunction(
                    self._observation_operator_fn,
                    input_shape=(),
                    output_shape=coords.shape,
                ),
                mean=self.coords2fn(coords.mean),
            )

        raise TypeError("Unsupported type of random variable for argument `coords`")

    def observation_operator(self, xs: np.ndarray) -> np.ndarray:
        return self._observation_operator_fn(xs)


class LinearInterpolationBasis(_basis.Basis):
    def __init__(
        self,
        domain: DomainLike,
        num_elements: int,
    ):
        super().__init__(size=num_elements + 2)

        self._domain = domains.asdomain(domain)

        self._grid = np.linspace(*self._domain, len(self))

        # TODO: Implement this as a `LinearOperator`
        self._observation_operator_fn = scipy.interpolate.interp1d(
            x=self._grid,
            y=np.eye(len(self)),
            kind="linear",
            axis=0,
            bounds_error=False,
            fill_value=0.0,
            assume_sorted=True,
        )

    @property
    def grid(self) -> np.ndarray:
        return self._grid

    def __getitem__(self, idx: int) -> pn.functions.Function:
        assert -len(self) <= idx < len(self)

        if idx < 0:
            idx += len(self)

        xs = self._grid[max(idx - 1, 0) : min(idx + 2, len(self))]

        if idx == 0:
            ys = (1.0, 0.0)
        elif idx == len(self) - 1:
            ys = (0.0, 1.0)
        else:
            ys = (0.0, 1.0, 0.0)

        ys = np.array(ys)

        return pn.functions.LambdaFunction(
            lambda x: np.interp(x, xs, ys),
            input_shape=(),
            output_shape=(),
        )

    def coords2fn(
        self,
        coords: Union[np.ndarray, pn.randvars.RandomVariable],
    ) -> Union[pn.functions.Function, pn.randprocs.RandomProcess]:
        if isinstance(coords, np.ndarray):
            return pn.functions.LambdaFunction(
                scipy.interpolate.interp1d(
                    x=self._grid,
                    y=coords,
                    kind="linear",
                    bounds_error=False,
                    fill_value=0.0,
                    assume_sorted=True,
                ),
                input_shape=(),
                output_shape=(),
            )

        # Interpret as random variable
        coords = pn.randvars.asrandvar(coords)

        if isinstance(coords, pn.randvars.Constant):
            return randprocs.DeterministicProcess(self.coords2fn(coords.support))

        if isinstance(coords, pn.randvars.Normal):
            return randprocs.ParametricGaussianProcess(
                weights=coords,
                feature_fn=pn.functions.LambdaFunction(
                    self._observation_operator_fn,
                    input_shape=(),
                    output_shape=coords.shape,
                ),
                mean=self.coords2fn(coords.mean),
            )

        raise TypeError("Unsupported type of random variable for argument `coords`")

    def observation_operator(self, xs: np.ndarray) -> np.ndarray:
        return self._observation_operator_fn(xs)
