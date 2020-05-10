from rider import default_pipeline


def test_default_pipeline(tmpdir):
    job = dict(
        url="https://github.com/epogrebnyak/rides-minimal/raw/master/sample_jsons/sample_jsons.zip",
        data_folder=tmpdir,
        days=None,
        types=None,
        limit=None,
    )
    trips_df, pairs_df = default_pipeline(**job)
    print(trips_df)
    print(pairs_df)
