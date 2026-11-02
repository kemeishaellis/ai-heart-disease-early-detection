
"""
Unit tests for the scikit-learn KMeans clustering protocol.

Project: AI Agentic Models for Early Detection and
Management of Heart Disease.

All test data are synthetic. No patient records are used.
"""

import numpy as np
import pytest
from sklearn.cluster import KMeans
from sklearn.exceptions import NotFittedError


def create_model(n_clusters=2, **kwargs):
    settings = {
        "n_clusters": n_clusters,
        "init": "k-means++",
        "n_init": 10,
        "random_state": 42,
        "algorithm": "lloyd",
    }
    settings.update(kwargs)
    return KMeans(**settings)


@pytest.fixture
def sample_data():
    return np.array([
        [0, 0],
        [0, 1],
        [10, 10],
        [10, 11],
    ], dtype=float)


def test_two_clear_clusters(sample_data):
    labels = create_model().fit_predict(sample_data)

    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[0] != labels[2]


def test_output_array_shape_dtype(sample_data):
    labels = create_model().fit_predict(sample_data)

    assert isinstance(labels, np.ndarray)
    assert labels.shape == (4,)
    assert np.issubdtype(labels.dtype, np.integer)


def test_cluster_centers(sample_data):
    model = create_model().fit(sample_data)
    centers = model.cluster_centers_
    centers = centers[np.argsort(centers[:, 0])]

    expected = np.array([
        [0, 0.5],
        [10, 10.5],
    ])

    np.testing.assert_allclose(
        centers, expected, atol=1e-6
    )
    assert model.inertia_ == pytest.approx(1.0)


def test_fit_returns_self(sample_data):
    model = create_model()

    result = model.fit(sample_data)

    assert result is model


def test_predict_new_points(sample_data):
    model = create_model().fit(sample_data)

    predictions = model.predict([
        [0, 0.2],
        [10, 10.8],
    ])

    assert predictions[0] == model.labels_[0]
    assert predictions[1] == model.labels_[2]


def test_single_cluster():
    data = np.array([
        [1, 1],
        [2, 2],
        [3, 3],
    ])

    model = create_model(n_clusters=1)
    labels = model.fit_predict(data)

    assert np.all(labels == 0)
    np.testing.assert_allclose(
        model.cluster_centers_,
        [[2, 2]],
    )


def test_duplicate_records():
    data = np.array([
        [0, 0],
        [0, 0],
        [10, 10],
        [10, 10],
    ])

    labels = create_model().fit_predict(data)

    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[0] != labels[2]


def test_single_feature():
    data = np.array([
        [0],
        [1],
        [10],
        [11],
    ])

    labels = create_model().fit_predict(data)

    assert labels.shape == (4,)
    assert labels[0] == labels[1]
    assert labels[2] == labels[3]


def test_synthetic_healthcare_metrics():
    data = np.array([
        [0.0, 0.0, 0.0],
        [0.1, 0.2, 0.1],
        [3.0, 3.0, 3.0],
        [3.1, 3.2, 3.1],
    ])

    labels = create_model().fit_predict(data)

    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[0] != labels[2]


def test_empty_input_raises():
    with pytest.raises(ValueError):
        create_model().fit([])


def test_nan_input_raises():
    data = np.array([
        [0.0],
        [np.nan],
        [10.0],
    ])

    with pytest.raises(ValueError):
        create_model().fit(data)


def test_non_numeric_input_raises():
    data = [["low"], ["high"], ["medium"]]

    with pytest.raises(ValueError):
        create_model().fit(data)


def test_too_many_clusters_raises():
    data = [[0, 0], [1, 1]]

    with pytest.raises(ValueError):
        create_model(n_clusters=3).fit(data)


def test_predict_before_fit_raises():
    model = create_model()

    with pytest.raises(NotFittedError):
        model.predict([[0, 1]])
