# Copyright (c) 2013, RedJack, LLC.
# All rights reserved.
#
# Please see the COPYING file in this distribution for license details.
import pytest


def pytest_configure(config):
    # Register the marks
    config.addinivalue_line(
        'markers',
        'log2exception: Replace the stderr output from `lawyerup.core.warn` '
        'and `lawyerup.core.error` with `tests.utils.Warning` and '
        '`tests.utils.Error` exceptions.')


@pytest.fixture(autouse=True)
def _log2exception_marker(request, monkeypatch):
    """
    Implement the log2exception marker.

    This will replace `lawyerup.core.warn` and `lawyerup.core.error`'s
    stderr output with `tests.utils.Warning` and `tests.utils.Error`
    exceptions.
    """
    marker = request.keywords.get('log2exception', None)

    if marker:
        import lawyerup.core
        from .utils import Warning, Error

        def warn_handler(msg):
            raise Warning(msg)

        def error_handler(msg, exit_code=1):
            raise Error(msg)

        monkeypatch.setattr(lawyerup.core, 'warn', warn_handler)
        monkeypatch.setattr(lawyerup.core, 'error', error_handler)
