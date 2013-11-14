"""
Tests for `lawyerup` as a command-line script.
"""
import pytest


pytestmark = pytest.mark.log2exception


def test_no_stdin():
    """
    `lawyerup <license> --context ...` should die with an error message
    if there are no paths on stdin.
    """
    from io import StringIO
    from lawyerup.core import main
    from test.utils import Error

    args = ['generic', '--context', 'organization=RedJack, LLC', 'year=2013']
    stdin = StringIO(u'\n'.join([u'', u'', u'']))

    with pytest.raises(Error) as e:
        main(args=args, stdin=stdin)
        assert e.message == 'No paths on stdin!'


def test_write_licenses_to_files(tmpdir):
    """
    `cat <list-of-files> | lawyerup <license> --context ...` should write
    the specified license header to all of the paths in <list-of-files>
    commented for the appropriate language.
    """
    from io import StringIO
    from lawyerup.core import main

    pyfile = tmpdir.join('test.py')
    pyfile_contents = u'\n'.join([
        u'#!/usr/bin/env python',
        u'',
        u'print "hello, world!"'])
    pyfile.write(pyfile_contents)

    cfile = tmpdir.join('test.c')
    cfile_contents = '\n'.join([
        u'/* -*- coding: utf-8 -*- */',
        u'#include<stdio.h>',
        u'',
        u'main () { printf("Hello World") }'])
    cfile.write(cfile_contents)

    stdin = StringIO(u'\n'.join([pyfile.strpath, cfile.strpath]))
    args = ['generic', '--context', 'organization=RedJack, LLC', 'year=2013']

    main(args=args, stdin=stdin)

    expected_pyfile = '\n'.join([
        '#!/usr/bin/env python',
        '# Copyright (c) 2013, RedJack, LLC.',
        '# All rights reserved.',
        '# ',
        '# Please see the COPYING file in this distribution for license details.',
        '',
        'print "hello, world!"'])
    assert pyfile.read() == expected_pyfile

    expected_cfile = '\n'.join([
        '/* -*- coding: utf-8 -*- */',
        '/*',
        ' * Copyright (c) 2013, RedJack, LLC.',
        ' * All rights reserved.',
        ' * ',
        ' * Please see the COPYING file in this distribution for license details.',
        ' */',
        '#include<stdio.h>',
        '',
        'main () { printf("Hello World") }'])
    assert cfile.read() == expected_cfile


def test_unknown_filetype(tmpdir):
    """
    `cat <list-of-files> | lawyerup <license> --context ...` should skip any
    files of unknown/unsupported filetypes with a warning message.
    """
    from io import StringIO
    from lawyerup.core import main
    from test.utils import Warning

    unknown = tmpdir.join('test.unknown')
    unknown_contents = u'\n'.join([
        u'#!/usr/bin/env python',
        u'',
        u'print "hello, world!"'])
    unknown.write(unknown_contents)

    stdin = StringIO(u'\n'.join([unknown.strpath]))
    args = ['generic', '--context', 'organization=RedJack, LLC', 'year=2013']

    with pytest.raises(Warning) as e:
        main(args=args, stdin=stdin)
        assert (e.message == 'could not determine filetype for "test.unknown". '
                             'skipping...')

    # File should not have changed
    assert unknown.read() == unknown_contents
