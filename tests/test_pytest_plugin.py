
pytest_plugins = 'pytester'


def test_flamegraph_plugin(testdir, tmp_path):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        import time
        def test_sth():
            time.sleep(0.5)
            assert "abc" == "abc"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--flamegraphs',
        f'--flamegraph-dir={tmp_path.absolute()}',
        '-v'
    )

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0

    svg_files = list(tmp_path.glob("*.svg"))
    assert len(svg_files) == 1
    assert svg_files[0].name == "test_sth.svg"
    with open(svg_files[0]) as f:
        assert "test_sth" in f.read()
