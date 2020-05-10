from rider import pipeline

import tempfile 
with tempfile.TemporaryDirectory() as tmpdirname:
    
    job = dict(
        url="https://github.com/epogrebnyak/rides-minimal/raw/master/sample_jsons/sample_jsons.zip",
        data_folder=tmpdirname,
        days=None,
        types=None,
        limit=None
    )
    
    (trips, routes, milages), (trips_df, pairs_df) = pipeline(**job)
    print(trips_df)
    print(pairs_df)
