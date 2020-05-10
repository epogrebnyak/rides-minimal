"""Графические функции для отрисовки треков"""

import matplotlib.pyplot as plt  # type: ignore
from matplotlib import cm  # type: ignore


def get_color(i, n):
    if n <= 10:
        cmap = cm.get_cmap(name="tab10")
        return cmap(i)
    else:
        cmap = cm.get_cmap(name="jet")
        return cmap(i / n)


def yield_route_and_color(routes):
    n = len(routes)
    for i, r in enumerate(routes):
        col = get_color(i, n)
        yield r, col


def make_plotter(axis_plotter_func):
    def plotter(routes, ax=None, title=""):
        if ax is None:
            f, ax = plt.subplots()
        n = len(routes)
        for i, r in enumerate(routes):
            col = get_color(i, n)
            axis_plotter_func(ax, r, col)
        ax.set_title(title)
        return ax

    return plotter


def scatter(ax, route, col):
    ax.scatter(x=route.lon, y=route.lat, s=0.5, alpha=0.8, color=col)


def segments(ax, route, col):
    ax.plot(route.lon, route.lat, lw=1, alpha=0.8, linestyle=":", color=col)


plot_points = make_plotter(scatter)
plot_connections = make_plotter(segments)


def plot_points_and_connections(routes, title="", ax=None):
    ax = plot_points(routes, ax)
    plot_connections(routes, ax)


def plot_raw_and_reduced(f1, f2, r1, r2, title="Общий заголовок"):
    fig, (ax1, ax2) = plt.subplots(
        nrows=1, ncols=2, figsize=(10, 4), sharex=True, sharey=True
    )
    plot_points_and_connections([f1, f2], ax=ax1, title="Исходные треки")
    plot_points_and_connections([r1, r2], ax=ax2, title="Упрощенные треки")
    plt.suptitle(title)


def plot_two(routes, i: int, j: int, simplify_with=None, title=""):
    """Отрисовка пары маршрутов по индексам в выборке."""
    f1, f2 = routes[i], routes[j]
    if simplify_with:
        r1, r2 = simplify_with(f1), simplify_with(f2)
    else:
        r1, r2 = f1, f2
    title = f"Поездки {i} и {j}"
    plot_raw_and_reduced(f1, f2, r1, r2, title)


def plot_one(route):
    return plot_points([route])
