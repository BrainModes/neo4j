from typing import Any
from typing import Callable
from typing import Collection
from typing import Dict
from typing import Tuple

import py2neo.database
import wrapt
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.trace import DbSystemValues
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.trace import Status
from opentelemetry.trace import StatusCode
from py2neo import Cursor
from py2neo import Transaction
from py2neo.client import ConnectionProfile

from app.opentelemetry.instrumentation.py2neo.package import _instruments
from app.opentelemetry.instrumentation.py2neo.version import __version__


class Py2NeoInstrumentor(BaseInstrumentor):
    """An instrumentor for py2neo Cypher queries."""

    def __init__(self):
        self.tracer = None

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwds) -> None:
        """Instrument py2neo Transaction class."""

        tracer_provider = kwds.get('tracer_provider')
        self._tracer = trace.get_tracer(__name__, __version__, tracer_provider)

        wrapt.wrap_function_wrapper(py2neo.database.work.Transaction, 'run', self._run)

    def _uninstrument(self, **kwds) -> None:
        """Remove instrumentation for py2neo Transaction class."""

        unwrap(py2neo.database.work.Transaction, 'run')

    def _run(self, func: Callable, instance: Transaction, args: Tuple, kwds: Dict[str, Any]) -> Cursor:
        """Wrap Transaction.run method execution with tracer span."""

        exception = None
        cypher = args[0]

        with self._tracer.start_as_current_span(cypher, kind=SpanKind.CLIENT) as span:
            if span.is_recording():
                connection_profile: ConnectionProfile = instance.graph.service.profile

                span_attributes = {
                    SpanAttributes.DB_SYSTEM: DbSystemValues.NEO4J.value,
                    SpanAttributes.DB_USER: connection_profile.user,
                    SpanAttributes.DB_STATEMENT: cypher,
                    SpanAttributes.NET_PEER_NAME: connection_profile.host,
                    SpanAttributes.NET_PEER_PORT: connection_profile.port,
                }

                for attribute, value in span_attributes.items():
                    span.set_attribute(attribute, value)

            try:
                result = func(*args, **kwds)
            except Exception as e:
                exception = e
                raise
            finally:
                if span.is_recording() and exception is not None:
                    span.set_status(Status(StatusCode.ERROR))

        return result
