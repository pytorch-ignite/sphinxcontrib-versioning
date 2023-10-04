"""Test calls to main() with different command line options."""

import time
from subprocess import CalledProcessError

import pytest

from sphinxcontrib_versioning.git import IS_WINDOWS


def test_sub_page_and_tag(tmpdir, local_docs, urls):
    """Test with sub pages and one git tag. Testing from local git repo.

    :param tmpdir: pytest fixture.
    :param local_docs: conftest fixture.
    :param urls: conftest fixture.
    """
    local_docs.ensure("subdir", "sub.rst").write(
        ".. _sub:\n" "\n" "Sub\n" "===\n" "\n" "Sub directory sub page documentation.\n"
    )
    local_docs.join("contents.rst").write("    subdir/sub\n", mode="a")
    pytest.run(local_docs, ["git", "add", "subdir", "contents.rst"])
    pytest.run(local_docs, ["git", "commit", "-m", "Adding subdir docs."])
    pytest.run(local_docs, ["git", "tag", "v1.0.0"])
    pytest.run(local_docs, ["git", "push", "origin", "main", "v1.0.0"])

    # Run.
    destination = tmpdir.ensure_dir("destination")
    output = pytest.run(
        local_docs, ["sphinx-versioning", "build", ".", str(destination), "-r", "main"]
    )
    assert "Traceback" not in output

    # Check root.
    urls(
        destination.join("contents.html"),
        [
            '<a href="main/contents.html">main</a>',
            '<a href="v1.0.0/contents.html">v1.0.0</a>',
        ],
    )
    urls(
        destination.join("subdir", "sub.html"),
        [
            '<a href="../main/subdir/sub.html">main</a>',
            '<a href="../v1.0.0/subdir/sub.html">v1.0.0</a>',
        ],
    )

    # Check main.
    urls(
        destination.join("main", "contents.html"),
        [
            '<a href="contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
        ],
    )
    urls(
        destination.join("main", "subdir", "sub.html"),
        [
            '<a href="sub.html">main</a>',
            '<a href="../../v1.0.0/subdir/sub.html">v1.0.0</a>',
        ],
    )

    # Check v1.0.0.
    urls(
        destination.join("v1.0.0", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="contents.html">v1.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.0.0", "subdir", "sub.html"),
        [
            '<a href="../../main/subdir/sub.html">main</a>',
            '<a href="sub.html">v1.0.0</a>',
        ],
    )


def test_moved_docs(tmpdir, local_docs, urls):
    """Test with docs being in their own directory.

    :param tmpdir: pytest fixture.
    :param local_docs: conftest fixture.
    :param urls: conftest fixture.
    """
    pytest.run(
        local_docs, ["git", "tag", "v1.0.0"]
    )  # Ignored since we only specify 'docs' in the command below.
    local_docs.ensure_dir("docs")
    pytest.run(local_docs, ["git", "mv", "conf.py", "docs/conf.py"])
    pytest.run(local_docs, ["git", "mv", "contents.rst", "docs/contents.rst"])
    pytest.run(local_docs, ["git", "commit", "-m", "Moved docs."])
    pytest.run(local_docs, ["git", "push", "origin", "main", "v1.0.0"])

    # Run.
    destination = tmpdir.join("destination")
    output = pytest.run(
        local_docs, ["sphinx-versioning", "build", "docs", str(destination), "-r", "main"]
    )
    assert "Traceback" not in output

    # Check main.
    urls(
        destination.join("contents.html"),
        ['<a href="main/contents.html">main</a>'],
    )
    urls(
        destination.join("main", "contents.html"),
        ['<a href="contents.html">main</a>'],
    )


def test_moved_docs_many(tmpdir, local_docs, urls):
    """Test with additional sources. Testing with --chdir. Non-created destination.

    :param tmpdir: pytest fixture.
    :param local_docs: conftest fixture.
    :param urls: conftest fixture.
    """
    pytest.run(local_docs, ["git", "tag", "v1.0.0"])
    local_docs.ensure_dir("docs")
    pytest.run(local_docs, ["git", "mv", "conf.py", "docs/conf.py"])
    pytest.run(local_docs, ["git", "mv", "contents.rst", "docs/contents.rst"])
    pytest.run(local_docs, ["git", "commit", "-m", "Moved docs."])
    pytest.run(local_docs, ["git", "tag", "v1.0.1"])
    local_docs.ensure_dir("docs2")
    pytest.run(local_docs, ["git", "mv", "docs/conf.py", "docs2/conf.py"])
    pytest.run(local_docs, ["git", "mv", "docs/contents.rst", "docs2/contents.rst"])
    pytest.run(local_docs, ["git", "commit", "-m", "Moved docs again."])
    pytest.run(local_docs, ["git", "tag", "v1.0.2"])
    pytest.run(
        local_docs, ["git", "push", "origin", "main", "v1.0.0", "v1.0.1", "v1.0.2"]
    )

    # Run.
    dest = tmpdir.join("destination")
    output = pytest.run(
        tmpdir,
        [
            "sphinx-versioning",
            "-c",
            str(local_docs),
            "build",
            "docs",
            "docs2",
            ".",
            str(dest),
            "-r",
            "main",
        ],
    )
    assert "Traceback" not in output

    # Check root.
    urls(
        dest.join("contents.html"),
        [
            '<a href="main/contents.html">main</a>',
            '<a href="v1.0.0/contents.html">v1.0.0</a>',
            '<a href="v1.0.1/contents.html">v1.0.1</a>',
            '<a href="v1.0.2/contents.html">v1.0.2</a>',
        ],
    )

    # Check main, v1.0.0, v1.0.1, v1.0.2.
    urls(
        dest.join("main", "contents.html"),
        [
            '<a href="contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="../v1.0.1/contents.html">v1.0.1</a>',
            '<a href="../v1.0.2/contents.html">v1.0.2</a>',
        ],
    )
    urls(
        dest.join("v1.0.0", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="contents.html">v1.0.0</a>',
            '<a href="../v1.0.1/contents.html">v1.0.1</a>',
            '<a href="../v1.0.2/contents.html">v1.0.2</a>',
        ],
    )
    urls(
        dest.join("v1.0.1", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="contents.html">v1.0.1</a>',
            '<a href="../v1.0.2/contents.html">v1.0.2</a>',
        ],
    )
    urls(
        dest.join("v1.0.2", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="../v1.0.1/contents.html">v1.0.1</a>',
            '<a href="contents.html">v1.0.2</a>',
        ],
    )


def test_version_change(tmpdir, local_docs, urls):
    """Verify new links are added and old links are removed when only changing versions. Using the same doc files.

    :param tmpdir: pytest fixture.
    :param local_docs: conftest fixture.
    :param urls: conftest fixture.
    """
    destination = tmpdir.join("destination")

    # Only main.
    output = pytest.run(
        local_docs, ["sphinx-versioning", "build", ".", "docs", str(destination), "-r", "main"]
    )
    assert "Traceback" not in output
    urls(
        destination.join("contents.html"),
        ['<a href="main/contents.html">main</a>'],
    )
    urls(
        destination.join("main", "contents.html"),
        ['<a href="contents.html">main</a>'],
    )

    # Add tags.
    pytest.run(local_docs, ["git", "tag", "v1.0.0"])
    pytest.run(local_docs, ["git", "tag", "v2.0.0"])
    pytest.run(local_docs, ["git", "push", "origin", "v1.0.0", "v2.0.0"])
    output = pytest.run(
        local_docs, ["sphinx-versioning", "build", ".", "docs", str(destination), "-r", "main"]
    )
    assert "Traceback" not in output
    urls(
        destination.join("contents.html"),
        [
            '<a href="main/contents.html">main</a>',
            '<a href="v1.0.0/contents.html">v1.0.0</a>',
            '<a href="v2.0.0/contents.html">v2.0.0</a>',
        ],
    )

    urls(
        destination.join("main", "contents.html"),
        [
            '<a href="contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="../v2.0.0/contents.html">v2.0.0</a>',
        ],
    )

    urls(
        destination.join("v1.0.0", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="contents.html">v1.0.0</a>',
            '<a href="../v2.0.0/contents.html">v2.0.0</a>',
        ],
    )

    urls(
        destination.join("v2.0.0", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="contents.html">v2.0.0</a>',
        ],
    )

    # Remove one tag.
    pytest.run(local_docs, ["git", "push", "origin", "--delete", "v2.0.0"])
    output = pytest.run(
        local_docs, ["sphinx-versioning", "build", ".", "docs", str(destination), "-r", "main"]
    )
    assert "Traceback" not in output
    urls(
        destination.join("contents.html"),
        [
            '<a href="main/contents.html">main</a>',
            '<a href="v1.0.0/contents.html">v1.0.0</a>',
        ],
    )

    urls(
        destination.join("main", "contents.html"),
        [
            '<a href="contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
        ],
    )

    urls(
        destination.join("v1.0.0", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="contents.html">v1.0.0</a>',
        ],
    )


@pytest.mark.usefixtures("local_docs")
def test_multiple_local_repos(tmpdir, urls):
    """Test from another git repo as the current working directory.

    :param tmpdir: pytest fixture.
    :param urls: conftest fixture.
    """
    other = tmpdir.ensure_dir("other")
    pytest.run(other, ["git", "init"])

    # Run.
    destination = tmpdir.ensure_dir("destination")
    output = pytest.run(
        other,
        ["sphinx-versioning", "-c", "../local", "-v", "build", ".", str(destination), "-r", "main"],
    )
    assert "Traceback" not in output

    # Check.
    urls(
        destination.join("contents.html"),
        ['<a href="main/contents.html">main</a>'],
    )
    urls(
        destination.join("main", "contents.html"),
        ['<a href="contents.html">main</a>'],
    )


@pytest.mark.parametrize("no_tags", [False, True])
def test_root_ref(tmpdir, local_docs, no_tags):
    """Test --root-ref and friends.

    :param tmpdir: pytest fixture.
    :param local_docs: conftest fixture.
    :param bool no_tags: Don't push tags. Test fallback handling.
    """
    local_docs.join("conf.py").write(
        'templates_path = ["_templates"]\n' 'html_sidebars = {"**": ["custom.html"]}\n'
    )
    local_docs.ensure("_templates", "custom.html").write(
        "<h3>Custom Sidebar</h3>\n"
        "<ul>\n"
        "<li>Current version: {{ current_version }}</li>\n"
        "</ul>\n"
    )
    pytest.run(local_docs, ["git", "add", "conf.py", "_templates"])
    pytest.run(local_docs, ["git", "commit", "-m", "Displaying version."])
    time.sleep(1.5)
    if not no_tags:
        pytest.run(local_docs, ["git", "tag", "v2.0.0"])
        time.sleep(1.5)
        pytest.run(local_docs, ["git", "tag", "v1.0.0"])
    pytest.run(local_docs, ["git", "checkout", "-b", "f2"])
    pytest.run(
        local_docs,
        ["git", "push", "origin", "main", "f2"]
        + ([] if no_tags else ["v1.0.0", "v2.0.0"]),
    )

    for arg, expected in (
        ("--root-ref=f2", "f2"),
        ("--greatest-tag", "v2.0.0"),
        ("--recent-tag", "v1.0.0"),
    ):
        # Run.
        dest = tmpdir.join("destination", arg[2:])
        default_root_ref = []
        if "root-ref" not in arg:
            default_root_ref += ["-r", "main"]
        output = pytest.run(
            tmpdir,
            [
                "sphinx-versioning",
                "-N",
                "-c",
                str(local_docs),
                "build",
                ".",
                str(dest),
                arg,
            ] + default_root_ref,
        )
        assert "Traceback" not in output
        # Check root.
        contents = dest.join("contents.html").read()
        if no_tags and expected != "f2":
            expected = "main"
        assert "Current version: {}".format(expected) in contents
        # Check warning.
        if no_tags and "tag" in arg:
            assert (
                "No git tags with docs found in remote. Falling back to --root-ref value."
                in output
            )
        else:
            assert (
                "No git tags with docs found in remote. Falling back to --root-ref value."
                not in output
            )
        # Check output.
        assert "Root ref is: {}".format(expected) in output


@pytest.mark.parametrize("parallel", [False, ])
def test_add_remove_docs(tmpdir, local_docs, urls, parallel):
    """Test URLs to other versions of current page with docs that are added/removed between versions.

    :param tmpdir: pytest fixture.
    :param local_docs: conftest fixture.
    :param urls: conftest fixture.
    :param bool parallel: Run sphinx-build with -j option.
    """
    if parallel and IS_WINDOWS:
        return pytest.skip("Sphinx parallel feature not available on Windows.")
    pytest.run(local_docs, ["git", "tag", "v1.0.0"])

    # Move once.
    local_docs.ensure_dir("sub")
    pytest.run(local_docs, ["git", "mv", "two.rst", "too.rst"])
    pytest.run(local_docs, ["git", "mv", "three.rst", "sub/three.rst"])
    local_docs.join("contents.rst").write(
        "Test\n"
        "====\n"
        "\n"
        "Sample documentation.\n"
        "\n"
        ".. toctree::\n"
        "    one\n"
        "    too\n"
        "    sub/three\n"
    )
    local_docs.join("too.rst").write(
        ".. _too:\n" "\n" "Too\n" "===\n" "\n" "Sub page documentation 2 too.\n"
    )
    pytest.run(local_docs, ["git", "commit", "-am", "Moved."])
    pytest.run(local_docs, ["git", "tag", "v1.1.0"])
    pytest.run(local_docs, ["git", "tag", "v1.1.1"])

    # Delete.
    pytest.run(local_docs, ["git", "rm", "too.rst", "sub/three.rst"])
    local_docs.join("contents.rst").write(
        "Test\n"
        "====\n"
        "\n"
        "Sample documentation.\n"
        "\n"
        ".. toctree::\n"
        "    one\n"
    )
    pytest.run(local_docs, ["git", "commit", "-am", "Deleted."])
    pytest.run(local_docs, ["git", "tag", "v2.0.0"])
    pytest.run(
        local_docs,
        ["git", "push", "origin", "v1.0.0", "v1.1.0", "v1.1.1", "v2.0.0", "main"],
    )

    # Run.
    destination = tmpdir.ensure_dir("destination")
    overflow = ["--", "-j", "2"] if parallel else []
    output = pytest.run(
        local_docs, ["sphinx-versioning", "build", ".", str(destination), "-r", "main"] + overflow
    )
    assert "Traceback" not in output

    # Check parallel.
    if parallel:
        assert "waiting for workers" in output
    else:
        assert "waiting for workers" not in output

    # Check root.
    urls(
        destination.join("contents.html"),
        [
            '<a href="main/contents.html">main</a>',
            '<a href="v1.0.0/contents.html">v1.0.0</a>',
            '<a href="v1.1.0/contents.html">v1.1.0</a>',
            '<a href="v1.1.1/contents.html">v1.1.1</a>',
            '<a href="v2.0.0/contents.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("one.html"),
        [
            '<a href="main/one.html">main</a>',
            '<a href="v1.0.0/one.html">v1.0.0</a>',
            '<a href="v1.1.0/one.html">v1.1.0</a>',
            '<a href="v1.1.1/one.html">v1.1.1</a>',
            '<a href="v2.0.0/one.html">v2.0.0</a>',
        ],
    )

    # Check main.
    urls(
        destination.join("main", "contents.html"),
        [
            '<a href="contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="../v1.1.0/contents.html">v1.1.0</a>',
            '<a href="../v1.1.1/contents.html">v1.1.1</a>',
            '<a href="../v2.0.0/contents.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("main", "one.html"),
        [
            '<a href="one.html">main</a>',
            '<a href="../v1.0.0/one.html">v1.0.0</a>',
            '<a href="../v1.1.0/one.html">v1.1.0</a>',
            '<a href="../v1.1.1/one.html">v1.1.1</a>',
            '<a href="../v2.0.0/one.html">v2.0.0</a>',
        ],
    )

    # Check v2.0.0.
    urls(
        destination.join("v2.0.0", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="../v1.1.0/contents.html">v1.1.0</a>',
            '<a href="../v1.1.1/contents.html">v1.1.1</a>',
            '<a href="contents.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v2.0.0", "one.html"),
        [
            '<a href="../main/one.html">main</a>',
            '<a href="../v1.0.0/one.html">v1.0.0</a>',
            '<a href="../v1.1.0/one.html">v1.1.0</a>',
            '<a href="../v1.1.1/one.html">v1.1.1</a>',
            '<a href="one.html">v2.0.0</a>',
        ],
    )

    # Check v1.1.1.
    urls(
        destination.join("v1.1.1", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="../v1.1.0/contents.html">v1.1.0</a>',
            '<a href="contents.html">v1.1.1</a>',
            '<a href="../v2.0.0/contents.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.1.1", "one.html"),
        [
            '<a href="../main/one.html">main</a>',
            '<a href="../v1.0.0/one.html">v1.0.0</a>',
            '<a href="../v1.1.0/one.html">v1.1.0</a>',
            '<a href="one.html">v1.1.1</a>',
            '<a href="../v2.0.0/one.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.1.1", "too.html"),
        [
            '<a href="../main/index.html">main</a>',
            '<a href="../v1.0.0/index.html">v1.0.0</a>',
            '<a href="../v1.1.0/too.html">v1.1.0</a>',
            '<a href="too.html">v1.1.1</a>',
            '<a href="../v2.0.0/index.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.1.1", "sub", "three.html"),
        [
            '<a href="../../main/index.html">main</a>',
            '<a href="../../v1.0.0/index.html">v1.0.0</a>',
            '<a href="../../v1.1.0/sub/three.html">v1.1.0</a>',
            '<a href="three.html">v1.1.1</a>',
            '<a href="../../v2.0.0/index.html">v2.0.0</a>',
        ],
    )

    # Check v1.1.0.
    urls(
        destination.join("v1.1.0", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="../v1.0.0/contents.html">v1.0.0</a>',
            '<a href="contents.html">v1.1.0</a>',
            '<a href="../v1.1.1/contents.html">v1.1.1</a>',
            '<a href="../v2.0.0/contents.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.1.0", "one.html"),
        [
            '<a href="../main/one.html">main</a>',
            '<a href="../v1.0.0/one.html">v1.0.0</a>',
            '<a href="one.html">v1.1.0</a>',
            '<a href="../v1.1.1/one.html">v1.1.1</a>',
            '<a href="../v2.0.0/one.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.1.0", "too.html"),
        [
            '<a href="../main/index.html">main</a>',
            '<a href="../v1.0.0/index.html">v1.0.0</a>',
            '<a href="too.html">v1.1.0</a>',
            '<a href="../v1.1.1/too.html">v1.1.1</a>',
            '<a href="../v2.0.0/index.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.1.0", "sub", "three.html"),
        [
            '<a href="../../main/index.html">main</a>',
            '<a href="../../v1.0.0/index.html">v1.0.0</a>',
            '<a href="three.html">v1.1.0</a>',
            '<a href="../../v1.1.1/sub/three.html">v1.1.1</a>',
            '<a href="../../v2.0.0/index.html">v2.0.0</a>',
        ],
    )

    # Check v1.0.0.
    urls(
        destination.join("v1.0.0", "contents.html"),
        [
            '<a href="../main/contents.html">main</a>',
            '<a href="contents.html">v1.0.0</a>',
            '<a href="../v1.1.0/contents.html">v1.1.0</a>',
            '<a href="../v1.1.1/contents.html">v1.1.1</a>',
            '<a href="../v2.0.0/contents.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.0.0", "one.html"),
        [
            '<a href="../main/one.html">main</a>',
            '<a href="one.html">v1.0.0</a>',
            '<a href="../v1.1.0/one.html">v1.1.0</a>',
            '<a href="../v1.1.1/one.html">v1.1.1</a>',
            '<a href="../v2.0.0/one.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.0.0", "two.html"),
        [
            '<a href="../main/index.html">main</a>',
            '<a href="two.html">v1.0.0</a>',
            '<a href="../v1.1.0/index.html">v1.1.0</a>',
            '<a href="../v1.1.1/index.html">v1.1.1</a>',
            '<a href="../v2.0.0/index.html">v2.0.0</a>',
        ],
    )
    urls(
        destination.join("v1.0.0", "three.html"),
        [
            '<a href="../main/index.html">main</a>',
            '<a href="three.html">v1.0.0</a>',
            '<a href="../v1.1.0/index.html">v1.1.0</a>',
            '<a href="../v1.1.1/index.html">v1.1.1</a>',
            '<a href="../v2.0.0/index.html">v2.0.0</a>',
        ],
    )


@pytest.mark.parametrize("verbosity", [0, 1, 3])
def test_passing_verbose(local_docs, urls, verbosity):
    """Test setting sphinx-build verbosity.

    :param local_docs: conftest fixture.
    :param urls: conftest fixture.
    :param int verbosity: Number of -v to use.
    """
    command = (
        ["sphinx-versioning"] + (["-v"] * verbosity) + ["build", ".", "destination", "-r", "main"]
    )

    # Run.
    output = pytest.run(local_docs, command)
    assert "Traceback" not in output

    # Check main.
    destination = local_docs.join("destination")
    urls(
        destination.join("contents.html"),
        ['<a href="main/contents.html">main</a>'],
    )
    urls(
        destination.join("main", "contents.html"),
        ['<a href="contents.html">main</a>'],
    )

    # Check output.
    if verbosity == 0:
        assert "INFO     sphinxcontrib_versioning.__main__" not in output
        assert "docnames to write:" not in output
    elif verbosity == 1:
        assert "INFO     sphinxcontrib_versioning.__main__" in output
        assert "docnames to write:" not in output
    else:
        assert "INFO     sphinxcontrib_versioning.__main__" in output
        assert "docnames to write:" in output


def test_whitelisting(local_docs, urls):
    """Test whitelist features.

    :param local_docs: conftest fixture.
    :param urls: conftest fixture.
    """
    pytest.run(local_docs, ["git", "tag", "v1.0"])
    pytest.run(local_docs, ["git", "tag", "v1.0-dev"])
    pytest.run(local_docs, ["git", "checkout", "-b", "included", "main"])
    pytest.run(local_docs, ["git", "checkout", "-b", "ignored", "main"])
    pytest.run(
        local_docs, ["git", "push", "origin", "v1.0", "v1.0-dev", "included", "ignored"]
    )

    command = [
        "sphinx-versioning",
        "-N",
        "build",
        ".",
        "html",
        "-w",
        "main",
        "-w",
        "included",
        "-W",
        "^v[0-9]+.[0-9]+$",
        "-r",
        "main",
    ]

    # Run.
    output = pytest.run(local_docs, command)
    assert "Traceback" not in output

    # Check output.
    assert "With docs: ignored included main v1.0 v1.0-dev" in output
    assert "Passed whitelisting: included main v1.0" in output

    # Check root.
    urls(
        local_docs.join("html", "contents.html"),
        [
            '<a href="included/contents.html">included</a>',
            '<a href="main/contents.html">main</a>',
            '<a href="v1.0/contents.html">v1.0</a>',
        ],
    )


@pytest.mark.parametrize("disable_banner", [False, True])
def test_banner(banner, local_docs, disable_banner):
    """Test the banner.

    :param banner: conftest fixture.
    :param local_docs: conftest fixture.
    :param bool disable_banner: Cause banner to be disabled.
    """
    pytest.run(local_docs, ["git", "tag", "snapshot-01"])
    local_docs.join("conf.py").write('project = "MyProject"\n', mode="a")
    pytest.run(local_docs, ["git", "commit", "-am", "Setting project name."])
    pytest.run(local_docs, ["git", "checkout", "-b", "stable", "main"])
    pytest.run(local_docs, ["git", "checkout", "main"])
    local_docs.join("conf.py").write('author = "me"\n', mode="a")
    pytest.run(local_docs, ["git", "commit", "-am", "Setting author name."])
    pytest.run(local_docs, ["git", "push", "origin", "main", "stable", "snapshot-01"])

    # Run.
    destination = local_docs.ensure_dir("..", "destination")
    args = [
        "--show-banner",
        "--banner-main-ref",
        "unknown" if disable_banner else "stable",
    ]
    output = pytest.run(
        local_docs, ["sphinx-versioning", "build", ".", str(destination), "-r", "main"] + args
    )
    assert "Traceback" not in output

    # Handle no banner.
    if disable_banner:
        assert "Disabling banner." in output
        assert "Banner main ref is" not in output
        banner(destination.join("contents.html"), None)
        return
    assert "Disabling banner." not in output
    assert "Banner main ref is: stable" in output

    # Check banner.
    banner(destination.join("stable", "contents.html"), None)  # No banner in main ref.
    for subdir in (False, True):
        banner(
            destination.join("main" if subdir else "", "contents.html"),
            "{}stable/contents.html".format("../" if subdir else ""),
            "the development version of MyProject. The main version is stable",
        )
    banner(
        destination.join("snapshot-01", "contents.html"),
        "../stable/contents.html",
        "an old version of Python. The main version is stable",
    )


def test_banner_css_override(banner, local_docs):
    """Test the banner CSS being present even if user overrides html_context['css_files'].

    :param banner: conftest fixture.
    :param local_docs: conftest fixture.
    """
    local_docs.join("conf.py").write(
        "html_context = {'css_files': ['_static/theme_overrides.css']}\n", mode="a"
    )
    local_docs.join("conf.py").write("html_static_path = ['_static']\n", mode="a")
    pytest.run(local_docs, ["git", "commit", "-am", "Setting override."])
    pytest.run(local_docs, ["git", "checkout", "-b", "other", "main"])
    pytest.run(local_docs, ["git", "push", "origin", "main", "other"])

    # Run.
    destination = local_docs.ensure_dir("..", "destination")
    output = pytest.run(
        local_docs,
        ["sphinx-versioning", "build", ".", str(destination), "--show-banner", "-r", "main"],
    )
    assert "Traceback" not in output
    # assert "Disabling banner." not in output
    # assert "Banner main ref is: main" in output

    # Check banner.
    banner(destination.join("main", "contents.html"), None)  # No banner in main ref.
    banner(
        destination.join("other", "contents.html"),
        "../main/contents.html",
        "the development version of Python. The main version is main",
    )

    # Check CSS.
    contents = destination.join("other", "contents.html").read()
    assert 'rel="stylesheet" href="_static/banner.css"' in contents
    assert destination.join("other", "_static", "banner.css").check(file=True)


def test_error_bad_path(tmpdir):
    """Test handling of bad paths.

    :param tmpdir: pytest fixture.
    """
    with pytest.raises(CalledProcessError) as exc:
        pytest.run(
            tmpdir,
            ["sphinx-versioning", "-N", "-c", "unknown", "build", ".", str(tmpdir)],
        )
    assert "Directory 'unknown' does not exist." in exc.value.output

    tmpdir.ensure("is_file")
    with pytest.raises(CalledProcessError) as exc:
        pytest.run(
            tmpdir,
            ["sphinx-versioning", "-N", "-c", "is_file", "build", ".", str(tmpdir)],
        )
    assert "Directory 'is_file' is a file." in exc.value.output

    with pytest.raises(CalledProcessError) as exc:
        pytest.run(tmpdir, ["sphinx-versioning", "-N", "build", ".", str(tmpdir)])
    assert (
        "Failed to find local git repository root in {}.".format(repr(str(tmpdir)))
        in exc.value.output
    )

    repo = tmpdir.ensure_dir("repo")
    pytest.run(repo, ["git", "init"])
    empty = tmpdir.ensure_dir("empty1857")
    with pytest.raises(CalledProcessError) as exc:
        pytest.run(
            repo,
            ["sphinx-versioning", "-N", "-g", str(empty), "build", ".", str(tmpdir)],
        )
    assert "Failed to find local git repository root in" in exc.value.output
    assert "empty1857" in exc.value.output


def test_error_no_docs_found(tmpdir, local):
    """Test no docs to build.

    :param tmpdir: pytest fixture.
    :param local: conftest fixture.
    """
    with pytest.raises(CalledProcessError) as exc:
        pytest.run(local, ["sphinx-versioning", "-N", "-v", "build", ".", str(tmpdir)])
    assert "No docs found in any remote branch/tag. Nothing to do." in exc.value.output


def test_error_bad_root_ref(tmpdir, local_docs):
    """Test bad root ref.

    :param tmpdir: pytest fixture.
    :param local_docs: conftest fixture.
    """
    with pytest.raises(CalledProcessError) as exc:
        pytest.run(
            local_docs,
            [
                "sphinx-versioning",
                "-N",
                "-v",
                "build",
                ".",
                str(tmpdir),
                "-r",
                "unknown",
            ],
        )
    assert "Root ref unknown not found in: main" in exc.value.output


def test_bad_banner(banner, local_docs):
    """Test bad banner main ref.

    :param banner: conftest fixture.
    :param local_docs: conftest fixture.
    """
    pytest.run(local_docs, ["git", "checkout", "-b", "stable", "main"])
    local_docs.join("conf.py").write("bad\n", mode="a")
    pytest.run(local_docs, ["git", "commit", "-am", "Breaking stable."])
    pytest.run(local_docs, ["git", "push", "origin", "stable"])

    # Run.
    destination = local_docs.ensure_dir("..", "destination")
    args = ["--show-banner", "--banner-main-ref", "stable"]
    output = pytest.run(
        local_docs, ["sphinx-versioning", "build", ".", str(destination), "-r", "main"] + args
    )
    assert "KeyError" not in output

    # Check no banner.
    assert "Banner main ref is: stable" in output
    assert "Banner main ref stable failed during pre-run." in output
    banner(destination.join("contents.html"), None)
