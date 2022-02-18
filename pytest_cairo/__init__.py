
try:
    from pytest_cairo import _version  # type: ignore
except ImportError:
    __version__ = 'unknown'
else:
    __version__ = _version.version
