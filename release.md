Multiexit Release
=================

#. Edit version::

    nano multiexit.py

#. Commit, tag::

    git commit -a
        chg: dev: Bumping version number to x.y.z.
    git tag x.y.z

#. Build wheel package::

    tox -e build

#. Push new revision and tag::

    git push
    git push --tags

#. Upload to PyPI::

    twine upload --username kuralabs --sign --identity info@kuralabs.io  dist/multiexit-x.y.z-py3-none-any.whl
