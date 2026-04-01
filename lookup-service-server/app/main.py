from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.elasticsearch import ElasticsearchInstrumentor
from .routers import records
from .routers import backward_record
import os
import logging
import subprocess, signal


app = FastAPI()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


logger.info("Starting the record conversion process to latest mapping")
process = subprocess.Popen(['python3', 'app/schedule_job.py'],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, #open('/var/log/perfsonar/pslookup-backward-compatibility-agent.log', 'w')
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    preexec_fn=(lambda: signal.signal(signal.SIGHUP, signal.SIG_IGN)))
        
continuous_pid = process.pid
logger.info("process started with pid {}".format(continuous_pid))


# Acquire a tracer
#trace.set_tracer_provider(TracerProvider())
#tracer = trace.get_tracer(__name__)

#if os.getenv('OTEL_COLLECTOR_ENDPOINT'):
#    trace_exporter = OTLPSpanExporter(endpoint="{}/v1/traces".format(os.getenv('OTEL_COLLECTOR_ENDPOINT')),
#                                      certificate_file=os.getenv('OTEL_COLLECTOR_CERT'), 
#                                      client_key_file=os.getenv('OTEL_COLLECTOR_CLIENT_KEY'), 
#                                      client_certificate_file=os.getenv('OTEL_COLLECTOR_CLIENT_CERT'), 
#                                      headers=os.getenv('OTEL_COLLECTOR_HEADERS'), 
#                                      timeout=os.getenv('OTEL_COLLECTOR_TIMEOUT'), 
#                                      compression=os.getenv('OTEL_COLLECTOR_COMPRESSION'), 
#                                      session=os.getenv('OTEL_COLLECTOR_SESSION')
#                                      )
#else:
#    trace_exporter = ConsoleSpanExporter()
#trace.get_tracer_provider().add_span_processor(
#    BatchSpanProcessor(trace_exporter))
#FastAPIInstrumentor().instrument_app(app)
#ElasticsearchInstrumentor().instrument()

app.include_router(records.router)
app.include_router(backward_record.router)