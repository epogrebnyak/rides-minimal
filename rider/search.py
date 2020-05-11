from dataclasses import dataclass
from typing import List, Tuple, Callable

import numpy as np  # type: ignore
from scipy.spatial.distance import cdist  # type: ignore
from tqdm import tqdm  # type: ignore

from rider.distance import safe_distance_2
from rider.routes import Route, points, DistanceFilter


def proximity(r1, r2):
    mat = cdist(points(r1), points(r2), safe_distance_2)
    return Proximity(mat)


@dataclass
class Proximity:
    """Матрица расстояний между двумя треками."""

    mat: np.ndarray

    def min(self):
        """
    Минимиальное расстояние между всеми точками двух треков.
    """
        return round(np.nanmin(self.mat), 3)

    def max(self):
        """
    Максимальное расстояние между всеми точками двух треков.
    """
        return round(np.amax(self.mat), 3)

    def side_min(self, axis: int):
        # 1 is to search by columns - applies to searching minima for 1st route
        # 0 is to search by rows - applies to searching minima for 2nd route
        x = np.nanmin(self.mat, axis)
        return x[~np.isnan(x)]

    def coverages(self):
        return Coverage(self.side_min(1)), Coverage(self.side_min(0))

    def report(self, search_radius: float):
        c1, c2 = self.coverages()
        return dict(
            min_dist=self.min(),
            max_dist=self.max(),
            cov_1=c1.coverage(search_radius),
            cov_2=c2.coverage(search_radius),
        )


@dataclass
class Coverage:
    """Для каждой точки выбранного трека посчитано 
       минимальное из расстояний до точек другого трека.
       
       Если в треке 10 точек, то минимальных расстояний 
       до другого трека будет 10.
       
       Мы выбираем те из расстояний, которые меньше заданного 
       порога(радиуса) сближения.
              
       Предположим в треке 10 точек и минимальные расстояния до 
       фигуры второго трека такие:
       
       >> mins = [21.2, 22.6, 17.6, 7.7, 2.7, 0.3, 0.4, 0.6, 0.2, 3.1]
       
       Тогда "сблизившимися" с другим треков при радиусе точности 1 
       мы считаем 4 точки:
       
       >> radius = 1           
       >> [x for x in mins if x < radius]
       [0.3, 0.4, 0.6, 0.2]
       
       Коэффциент перекрытия составляет 4/10 = 40%. 
       
       Он показывает, что 40% точек данного трека
       находились на расстоянии не более чем *radius*
       от какой-то точки другого трека.
       
       Замечания:
       
       - Коэффциент перекрытия (КП) может интепретироваться как 
         часть пути, если отрезки между точками равные. 
         
       - Значение коэффциента перекрытия зависит от точности 
         апроксимации трека и радиуса.       
         
       - Треки могут иметь сложную форму, высокий КП не гарантирует,
         что доставку по одному треку можно переложить на другой трек.
         Но при низких КП это заведомо невозможно.
         
       - Нулевой КП - машины ездили в разных местах.  
         
    """

    mins: np.ndarray

    def in_proximity(self, radius: float):
        """
           Количество точек с минимальными расстояниями до другого трека.
           Минималаьное расстояние - это расстояние, величина которого
           меньше заданного радиуса сближения.
        """
        return (self.mins < radius).sum()  # self.mins[self.mins < radius]

    def coverage(self, radius: float):
        """
           Коэффициент перекрытия - доля трека, которая находится 
           на расстоянии не более заданного радиуса от другого трека.
        """
        return round(self.in_proximity(radius) / len(self.mins), 2)


from itertools import combinations


def get_combinations(n: int) -> List[Tuple[int, int]]:
    """Выбор комбинаций из n по 2."""
    return [(i, j) for i, j in combinations(range(n), 2)]


def count_combinations(n: int) -> int:
    return len(list(get_combinations(n)))


def search(
    routes: List[Route],
    simplify_with: Callable,
    search_radius_1: float,
    refine_with=Callable,
    search_radius_2=float,
    limit=None,
):

    # Урезаем для демо-примеров
    if limit:
        routes = routes[0:limit]
        print(f"Trimmed dataset to {limit} pairs")

    m = len(routes)
    print(f"{count_combinations(m)} pairs are possible for {m} routes")

    # Грубая апроксимация треков
    print(f"Simplified {m} routes")
    rough_routes = [simplify_with(route) for route in routes]

    def prox(i, j):  # замыкание для удобного доступа к routes
        return proximity(rough_routes[i], rough_routes[j])

    # Выбор пересекающися пар
    pairs = [
        (i, j) for (i, j) in get_combinations(m) if prox(i, j).min() < search_radius_1
    ]
    print(f"Found {len(pairs)} pairs of intersecting routes")

    # Уточняем апроксимацию треков
    def members(pairs):
        from itertools import chain

        return set(chain.from_iterable(pairs))

    refined_routes = list(range(m))
    for k, i in enumerate(members(pairs)):
        refined_routes[i] = refine_with(routes[i])
    print(f"Made better approximation of {k} routes")
    print("Calculating distances between routes and reporting...")

    # Считаем перекрытие треков в пересекающися парах

    result = []
    for (i, j) in tqdm(pairs):
        p = proximity(refined_routes[i], refined_routes[j])
        if p.min() < search_radius_2:
            d = dict(id_1=i, id_2=j, **p.report(search_radius_2))
            result.append(d)
    return result


DEFAULT_PARAM = dict(
    simplify_with=DistanceFilter(n_segments=10).callable,
    search_radius_1=10,
    refine_with=DistanceFilter(step_km=2.5).callable,
    search_radius_2=2.5 * 1.2,
)


def default_search(routes: List[Route], limit=None):
    return search(routes, limit=limit, **DEFAULT_PARAM)
