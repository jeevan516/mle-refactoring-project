from king_county.pipeline import FEATURES, make_feature_pipeline, prepare_data


def test_prepare_data_reproduces_the_notebook_dataset():
    df = prepare_data()
    # 21,597 raw sales minus the 33-bedroom record.
    assert df.shape == (21596, 23)
    assert not df.isna().any().any()
    assert set(FEATURES) <= set(df.columns)
    assert df["bedrooms"].max() < 33


def test_feature_pipeline_returns_model_features_for_every_row(raw_houses):
    features = make_feature_pipeline().fit_transform(raw_houses)
    assert list(features.columns) == FEATURES
    assert len(features) == len(raw_houses)
    assert not features.isna().any().any()


def test_feature_pipeline_does_not_need_the_price(raw_houses):
    pipeline = make_feature_pipeline().fit(raw_houses)
    new_house = raw_houses.drop(columns=["price"]).head(1)
    assert len(pipeline.transform(new_house)) == 1
