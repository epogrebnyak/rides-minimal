from search import (
    get_dataframe,
    get_trips,
    distance_increment,
    report_proximity,
)


def pair(trips, i, j, simplify_with, search_radius):
    t1, t2 = trips[i], trips[j]
    r1, r2 = [simplify_with(t.route) for t in (t1, t2)]
    prox = report_proximity(r1, r2, search_radius)
    return dict(track_ids=[i, j], milage_km=[t1.milage, t2.milage], **prox)


df = get_dataframe("one_day.zip")
trips = get_trips(df)
res = pair(
    trips,
    i=32,
    j=46,
    simplify_with=distance_increment(step_km=0.1),
    search_radius=0.010,
)
print(res)

# track_ids [32, 46]
# milage_km [48.773, 27.98]
# approximated_with {'func': 'distance_increment', 'arg': 0.1}
# distances {'min': 0.001, 'max': 7.26}
# search_radius 0.01
# coverage [0.16, 0.2]
