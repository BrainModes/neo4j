from unittest.mock import Mock

import pytest
from opentelemetry.trace import INVALID_SPAN
from opentelemetry.trace import SpanKind
from py2neo import Transaction

from app.opentelemetry.instrumentation.py2neo import Py2NeoInstrumentor


@pytest.fixture
def transaction():
    class Profile(Mock):
        protocol = 'bolt'

    class Connector(Mock):
        @property
        def profile(self):
            return Profile()

        def run_in_tx(self, *args, **kwds):
            return []

    class Graph(Mock):
        @property
        def service(self):
            return self

        @property
        def connector(self):
            return Connector()

    yield Transaction(Graph())


@pytest.fixture
def py2neo_instrumentor():
    yield Py2NeoInstrumentor()


class TestPy2NeoInstrumentor:
    def test_instrumentor_wraps_py2neo_transaction_run_method_with_tracer_span(
        self, faker, py2neo_instrumentor, transaction, mocker
    ):
        py2neo_instrumentor.instrument()

        mock_start_as_current_span = mocker.patch.context_manager(
            py2neo_instrumentor._tracer, 'start_as_current_span', return_value=INVALID_SPAN
        )

        expected_cypher = faker.pystr()

        transaction.run(expected_cypher)

        mock_start_as_current_span.assert_called_once_with(expected_cypher, kind=SpanKind.CLIENT)

        py2neo_instrumentor.uninstrument()
