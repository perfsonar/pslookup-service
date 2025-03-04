from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from .routers import records
import os

app = FastAPI()

# Acquire a tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

if os.getenv('OTEL_APM_EXPORT'):
    trace_exporter = OTLPSpanExporter(endpoint="http://localhost:4318")
else:
    trace_exporter = ConsoleSpanExporter()
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(trace_exporter))
FastAPIInstrumentor().instrument_app(app)
ElasticsearchInstrumentor().instrument()

app.include_router(records.router)
