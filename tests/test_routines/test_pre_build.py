"""Test function in module."""

import posixpath

import py
import pytest

from sphinxcontrib_versioning.lib import HandledError
from sphinxcontrib_versioning.routines import gather_git_info, pre_build
from sphinxcontrib_versioning.versions import Versions


def test_single(local_docs):
    """With single version.

    :param local_docs: conftest fixture.
    """
    versions = Versions(gather_git_info(str(local_docs), ["conf.py"], tuple(), tuple()))
    assert len(versions) == 1

    # Run and verify directory.
    exported_root = py.path.local(pre_build(str(local_docs), versions))
    assert len(exported_root.listdir()) == 1
    assert exported_root.join(versions["main"]["sha"], "conf.py").read() == ""

    # Verify root_dir and main_doc..
    expected = ["main/contents"]
    assert (
        sorted(posixpath.join(r["root_dir"], r["main_doc"]) for r in versions.remotes)
        == expected
    )


def test_dual(local_docs):
    """With two versions, one with main_doc defined.

    :param local_docs: conftest fixture.
    """
    pytest.run(local_docs, ["git", "checkout", "feature"])
    local_docs.join("conf.py").write('main_doc = "index"\n')
    local_docs.join("index.rst").write("Test\n" "====\n" "\n" "Sample documentation.\n")
    pytest.run(local_docs, ["git", "add", "conf.py", "index.rst"])
    pytest.run(local_docs, ["git", "commit", "-m", "Adding docs with main_doc"])
    pytest.run(local_docs, ["git", "push", "origin", "feature"])

    versions = Versions(gather_git_info(str(local_docs), ["conf.py"], tuple(), tuple()))
    assert len(versions) == 2

    # Run and verify directory.
    exported_root = py.path.local(pre_build(str(local_docs), versions))
    assert len(exported_root.listdir()) == 2
    assert exported_root.join(versions["main"]["sha"], "conf.py").read() == ""
    assert (
        exported_root.join(versions["feature"]["sha"], "conf.py").read()
        == 'main_doc = "index"\n'
    )

    # Verify versions root_dirs and main_docs.
    expected = ["feature/index", "main/contents"]
    assert (
        sorted(posixpath.join(r["root_dir"], r["main_doc"]) for r in versions.remotes)
        == expected
    )


def test_file_collision(local_docs):
    """Test handling of filename collisions between generates files from root and branch names.

    :param local_docs: conftest fixture.
    """
    pytest.run(local_docs, ["git", "checkout", "-b", "_static"])
    pytest.run(local_docs, ["git", "push", "origin", "_static"])

    versions = Versions(gather_git_info(str(local_docs), ["conf.py"], tuple(), tuple()))
    assert len(versions) == 2

    # Verify versions root_dirs and main_docs.
    pre_build(str(local_docs), versions)
    expected = ["_static_/contents", "main/contents"]
    assert (
        sorted(posixpath.join(r["root_dir"], r["main_doc"]) for r in versions.remotes)
        == expected
    )


def test_invalid_name(local_docs):
    """Test handling of branch names with invalid root_dir characters.

    :param local_docs: conftest fixture.
    """
    pytest.run(local_docs, ["git", "checkout", "-b", "robpol86/feature"])
    pytest.run(local_docs, ["git", "push", "origin", "robpol86/feature"])

    versions = Versions(gather_git_info(str(local_docs), ["conf.py"], tuple(), tuple()))
    assert len(versions) == 2

    # Verify versions root_dirs and main_docs.
    pre_build(str(local_docs), versions)
    expected = ["main/contents", "robpol86_feature/contents"]
    assert (
        sorted(posixpath.join(r["root_dir"], r["main_doc"]) for r in versions.remotes)
        == expected
    )


def test_error(config, local_docs):
    """Test with a bad root ref. Also test skipping bad non-root refs.

    :param config: conftest fixture.
    :param local_docs: conftest fixture.
    """
    pytest.run(local_docs, ["git", "checkout", "-b", "a_good", "main"])
    pytest.run(local_docs, ["git", "checkout", "-b", "c_good", "main"])
    pytest.run(local_docs, ["git", "checkout", "-b", "b_broken", "main"])
    local_docs.join("conf.py").write("main_doc = exception\n")
    pytest.run(local_docs, ["git", "commit", "-am", "Broken version."])
    pytest.run(local_docs, ["git", "checkout", "-b", "d_broken", "b_broken"])
    pytest.run(
        local_docs,
        ["git", "push", "origin", "a_good", "b_broken", "c_good", "d_broken"],
    )

    versions = Versions(
        gather_git_info(str(local_docs), ["conf.py"], tuple(), tuple()), sort=["alpha"]
    )
    assert [r["name"] for r in versions.remotes] == [
        "a_good",
        "b_broken",
        "c_good",
        "d_broken",
        "main",
    ]

    # Bad root ref.
    config.root_ref = "b_broken"
    with pytest.raises(HandledError):
        pre_build(str(local_docs), versions)

    # Remove bad non-root refs.
    config.root_ref = "main"
    pre_build(str(local_docs), versions)
    assert [r["name"] for r in versions.remotes] == ["a_good", "c_good", "main"]
