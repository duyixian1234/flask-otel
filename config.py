import logging
import logging.config

from opentelemetry import trace


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        setattr(
            record,
            "traceId",
            f"{trace.get_current_span().get_span_context().trace_id:x}"[:7],
        )
        return True


def configure_logging():
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s][%(levelname)s][%(name)s][%(traceId)s]: %(message)s"
                }
            },
            "filters": {"context": {"()": ContextFilter}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["context"],
                }
            },
            "loggers": {
                "": {"handlers": ["console"], "level": "INFO"},
            },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            },
        }
    )
