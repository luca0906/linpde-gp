import numpy as np

from linpde_gp.linfuncops import LinearFunctionOperator

from ._arithmetic import ScaledProcessVectorCrossCovariance
from .linfunctls._dirac import Kernel_Dirac_Indentity, Kernel_Identity_Dirac


@LinearFunctionOperator.__call__.register  # pylint: disable=no-member
def _(
    self, pv_crosscov: ScaledProcessVectorCrossCovariance, /
) -> ScaledProcessVectorCrossCovariance:
    return ScaledProcessVectorCrossCovariance(
        pv_crosscov=self(pv_crosscov._pv_crosscov),
        scalar=pv_crosscov._scalar,
    )


@LinearFunctionOperator.__call__.register(  # pylint: disable=no-member
    Kernel_Identity_Dirac
)
def _(self, pv_crosscov: Kernel_Identity_Dirac, /) -> np.ndarray:
    return Kernel_Identity_Dirac(
        self(pv_crosscov.kernel, argnum=0),
        pv_crosscov.dirac,
    )


@LinearFunctionOperator.__call__.register(  # pylint: disable=no-member
    Kernel_Dirac_Indentity
)
def _(self, pv_crosscov: Kernel_Dirac_Indentity, /) -> np.ndarray:
    return Kernel_Dirac_Indentity(
        self(pv_crosscov, argnum=1),
        pv_crosscov.dirac,
    )
