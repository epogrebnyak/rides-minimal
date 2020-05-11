from rider import default_pipeline


def test_default_pipeline(tmpdir):
    job = dict(
        url="https://github.com/epogrebnyak/rides-minimal/raw/master/sample_jsons/sample_jsons.zip",
        data_folder=tmpdir,
        days=None,
        types=["passenger"],
        limit=None,
    )
    (trips_df, pairs_df), _ = default_pipeline(**job)
    print(trips_df)
    print(pairs_df)
    assert len(trips_df) == 3
    assert len(pairs_df) == 3
