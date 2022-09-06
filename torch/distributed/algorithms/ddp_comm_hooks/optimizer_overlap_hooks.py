from typing import Any, Callable

import torch
import torch.distributed as dist
import os

_FUNCTIONAL_OPTIM_STEP_METHOD_NAME = "step_param"

class _OptimizerHookState(object):
    """
    Holds state for running optimizer in-line after DDP communication hook.
    Currently contains only optimizer class which must have a method `step_param`.
    """

    __slots__ = [
        "functional_optimizer",
        "params_to_optimize",
        "set_grads_to_none"
    ]

    def __init__(self, functional_optim, params=None, set_grads_to_none=False):
        self.functional_optimizer = functional_optim
        self._check_valid_functional_optim()
        self._set_params_to_optimize(params)
        self.set_grads_to_none = set_grads_to_none

    def _set_params_to_optimize(self, params):
        if params is not None:
            self.params_to_optimize = set(params)

    def _check_valid_functional_optim(self):
        if not hasattr(self.functional_optimizer, _FUNCTIONAL_OPTIM_STEP_METHOD_NAME):
            raise ValueError(
                f"Class {type(self.functional_optimizer)} must implement method "
                f"{_FUNCTIONAL_OPTIM_STEP_METHOD_NAME}."
            )


def _hook_then_optimizer(
    hook: Callable[[Any, dist.GradBucket], torch.futures.Future[torch.Tensor]],
    optimizer_state: _OptimizerHookState,
) -> Callable[[Any, dist.GradBucket], torch.futures.Future[torch.Tensor]]:
    r"""
    Runs optimizer in a functional fashion after DDP communication hook.
    """
    has_set_params = (
        hasattr(optimizer_state, 'params_to_optimize')
        and optimizer_state.params_to_optimize is not None
    )

    set_grads_to_none = optimizer_state.set_grads_to_none

    def hook_then_optimizer_wrapper(
        hook_state, bucket: dist.GradBucket
    ) -> torch.futures.Future[torch.Tensor]:
        # Run original hook
        fut = hook(hook_state, bucket)

        def optimizer_step(fut):
            gradient_tensors = bucket.gradients()
            model_params = bucket.parameters()
            for grad_tensor, model_param in zip(gradient_tensors, model_params):
                if not has_set_params or model_param in optimizer_state.params_to_optimize:
                    optimizer_state.functional_optimizer.step_param(
                        model_param,
                        grad_tensor,
                    )
                    nonlocal set_grads_to_none
                    if set_grads_to_none:
                        model_param.grad = None

            return bucket.buffer()
        return fut.then(optimizer_step)

    return hook_then_optimizer_wrapper
