"""Temporary failure to demonstrate required checks after protecting main."""


def test_intentional_ci_failure():
    assert False, "Intentional CI failure: verify required checks block merging."
