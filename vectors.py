"""Функции для уменьшения количества точек в треке"""


def equitime(t, step_min=5):
  """Взять равные промежутки по *step_min* минут времени."""
  time = step_min/60
  ix = growing_index(t.duration, time)
  return t.iloc[ix,:]

def equidist(t, step_km):
  """Взять равные промежутки по *step_km* расстояния."""
  ix = growing_index(t.milage, step_km)
  return t.iloc[ix,:]

def equitime(t, step_min=5):
  """Взять равные промежутки по *step_min* минут времени."""
  time = step_min/60
  ix = growing_index(t.duration, time)
  return t.iloc[ix,:]

def spaced_dist(t, n: int, start=False, end=False):
  """Взять *n* равных промежутков по расстоянию.
  Опционально исключить начало и конец трека.
  """
  ix = percentile_index(t.milage, qs(n, start, end))
  return t.iloc[ix,:]

def spaced_time(t, n: int, start=False, end=False):
  """Взять *n* равных промежутков по времени.
  Опционально исключить начало и конец трека.
  """
  ix = percentile_index(t.duration, qs(n, start, end))
  return t.iloc[ix,:]


def growing_index(xs, step):    
    xs = [x for x in xs]
    result = [0] # will include start point
    current = xs[0]
    for i, x in enumerate(xs):
        accumulated = x - current
        if accumulated >= step:
            result.append(i)
            accumulated = 0
            current = x
    if result[-1] != len(xs): # will include end point
        result.append(len(xs))
    return result


def midpoint(xs, p):
    return p * (xs[-1] - xs[0]) + xs[0]


def qs(n, start=False, end=False):
    step = 1 / n
    gen = range(0 if start else 1, n + (1 if end else 0))
    return [step * i for i in gen]


def percentile_index(xs, ps):
    xs = [x for x in xs]
    res = []
    ps = ps if isinstance(ps, list) else [ps]
    p_stream = iter(ps)
    p = next(p_stream)
    v = midpoint(xs, p)
    for i, x in enumerate(xs):
        if x >= v:
            res.append(i)
            try:
                p = next(p_stream)
                v = midpoint(xs, p)
            except StopIteration:
                break
            continue
    return res
