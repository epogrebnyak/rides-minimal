from search import (
    get_dataframe,
    yield_trips,
    simplify,
    report_proximity,
    distance_increment,
)


df = get_dataframe()
trips = list(yield_trips(df))
i, j = 32, 46
step_km = 0.1
search_radius = 0.010
t1 = trips[i]
t2 = trips[j]
r1, r2 = simplify([t1.route, t2.route], distance_increment(step_km))
prox = report_proximity(r1, r2, search_radius)
res = dict(
    track_ids=[i, j],
    milage_km=[t1.milage, t2.milage],
    approximated_with=dict(func="distance_increment", arg=step_km),
    **prox
)
for k, v in res.items():
    print(k, v)

# track_ids [32, 46]
# milage_km [48.773, 27.98]
# approximated_with {'func': 'distance_increment', 'arg': 0.1}
# distances {'min': 0.001, 'max': 7.26}
# search_radius 0.01
# coverage [0.16, 0.2]
