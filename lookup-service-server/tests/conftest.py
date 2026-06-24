import os
import sys
import pytest

os.environ.setdefault('ELASTIC_HOST', 'http://localhost:9200')
os.environ.setdefault('ELASTIC_USER', 'user')
os.environ.setdefault('ELASTIC_PASS', 'pass')
os.environ.setdefault('ELASTIC_INDEX', 'test-index')
os.environ.setdefault('ELASTIC_V1_INDEX', 'test-v1-index')
os.environ.setdefault('ELASTIC_VERIFY_CERTS', 'false')
os.environ.setdefault('V1_LOG_DIR', '/tmp')


@pytest.fixture(scope='session', autouse=True)
def add_app_to_path():
    _app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
    sys.path.insert(0, _app_dir)
    yield
    sys.path.remove(_app_dir)
