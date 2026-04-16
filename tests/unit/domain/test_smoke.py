"""Smoke test to verify the package is importable."""


def test_package_is_importable() -> None:
    import aihelm

    assert aihelm is not None
