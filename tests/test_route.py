import pandas as pd

# Created via:
# routes[0].sample(20).sort_values("time", ascending=True).to_dict()

r_ = pd.DataFrame(
    {
        "lat": {
            7083240: 54.6144833333,
            7083361: 54.6160766667,
            7083672: 54.6137366667,
            7083696: 54.61563,
            7083745: 54.61434499999999,
            7083876: 54.6155783333,
            7084000: 54.6144483333,
            7084085: 54.623331666700004,
            7084185: 54.6223866667,
            7084303: 54.6149283333,
            7084354: 54.61444,
            7084676: 54.6145,
            7084680: 54.614430000000006,
            7084754: 54.617805000000004,
            7084765: 54.61681,
            7084805: 54.6146166667,
            7084942: 54.6144166667,
            7085089: 54.6151766667,
            7085292: 54.6162433333,
            7085403: 54.614385,
        },
        "lon": {
            7083240: 21.215865,
            7083361: 21.1001,
            7083672: 21.1272133333,
            7083696: 21.171521666700002,
            7083745: 21.2189866667,
            7083876: 21.2050516667,
            7084000: 21.21761,
            7084085: 21.235075,
            7084185: 21.23394,
            7084303: 21.208285,
            7084354: 21.2159483333,
            7084676: 21.21568,
            7084680: 21.2159333333,
            7084754: 21.2331766667,
            7084765: 21.2345866667,
            7084805: 21.2403416667,
            7084942: 21.2181033333,
            7085089: 21.207001666700002,
            7085292: 21.20059,
            7085403: 21.218420000000002,
        },
        "time": {
            7083240: 1568016180,
            7083361: 1568016845,
            7083672: 1568019770,
            7083696: 1568019930,
            7083745: 1568020123,
            7083876: 1568022911,
            7084000: 1568023266,
            7084085: 1568023650,
            7084185: 1568026797,
            7084303: 1568027769,
            7084354: 1568028340,
            7084676: 1568031743,
            7084680: 1568031749,
            7084754: 1568031955,
            7084765: 1568031996,
            7084805: 1568032149,
            7084942: 1568032643,
            7085089: 1568033924,
            7085292: 1568034834,
            7085403: 1568037032,
        },
    }
)

from rider.routes import make_route, Segments, Increment

r = make_route(r_)


def test_milage():
    assert r.milage == 26.38


def test_distance_filter():
    assert Segments.by_distance(n=10)(r).__len__() == 11
    assert Increment.by_distance(step_km=2.5)(r).__len__() == 8
