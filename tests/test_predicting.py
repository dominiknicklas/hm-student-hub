import pytest
from student_hub.predicting import is_toxic

def test_is_toxic_returns_true_if_score_above_threshold(mocker):
    # Mock the models predict call to return a toxic score
    mocker.patch("student_hub.predicting.predict_toxicity", return_value={
        "toxic": 0.41,
        "severe_toxic": 0.1,
        "obscene": 0.05,
        "threat": 0.0,
        "insult": 0.2,
        "identity_hate": 0.0,
    })

    assert is_toxic("Some toxic comment") == True


def test_is_toxic_returns_false_if_all_scores_below_threshold(mocker):
    # Mock the models predict call to return a non toxic score
    mocker.patch("student_hub.predicting.predict_toxicity", return_value={
        "toxic": 0.2,
        "severe_toxic": 0.1,
        "obscene": 0.05,
        "threat": 0.0,
        "insult": 0.2,
        "identity_hate": 0.0,
    })

    assert is_toxic("Some clean comment") == False
