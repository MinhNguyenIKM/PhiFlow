import numpy as np
from numbers import Number

from phi import struct
from phi.struct.functions import mappable
from .base import NoBackendFound
from .nd import fftfreq
from .backend import backend as math


@mappable(item_condition=struct.VARIABLES, anytype_context=True)
def types(x):
    try:
        return math.dtype(x)
    except NoBackendFound:
        return type(x)


def is_static_shape(obj):
    if not isinstance(obj, (tuple, list, np.ndarray)):
        return False
    for element in obj:
        if not isinstance(element, Number) and element is not None:
            return False
    return True


def _none_to_one(shape):
    result = list(map(lambda val: 1 if val is None else val, shape))
    return result


@mappable(leaf_condition=is_static_shape)
def zeros(shape, dtype=np.float32):
    return np.zeros(_none_to_one(shape), dtype=dtype)


def zeros_like(object):
    f = lambda tensor: math.zeros_like(tensor)
    return struct.map(f, object, leaf_condition=is_static_shape)


@mappable(leaf_condition=is_static_shape)
def ones(shape, dtype=np.float32):
    return np.ones(_none_to_one(shape), dtype)


@mappable(leaf_condition=is_static_shape)
def randn(shape, dtype=np.float32):
    return np.random.randn(*_none_to_one(shape)).astype(dtype)


def randfreq(shape, dtype=np.float32, power=8):
    def genarray(shape):
        fft = randn(shape, dtype) + 1j * randn(shape, dtype)
        k = fftfreq(shape[1:-1], mode='absolute')
        shape_fac = math.sqrt(math.mean(shape[1:-1]))  # 16: 4, 64: 8, 256: 24,
        fft *= (1 / (k + 1)) ** power * power * shape_fac
        array = math.ifft(fft)
        array = array.astype(dtype)
        return array
    return struct.map(genarray, shape, leaf_condition=is_static_shape)