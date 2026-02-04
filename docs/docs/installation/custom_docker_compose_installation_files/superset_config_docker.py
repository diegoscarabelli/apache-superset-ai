# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# This file overrides the superset/docker/pythonpath_dev/superset_config.py file, in which it is imported
# as a final step as a means to override "defaults".

import os

from celery.schedules import crontab

# Feature flags to enable or disable specific Superset features
FEATURE_FLAGS = {
    "ALERT_REPORTS": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
    "TAGGING_SYSTEM": True,
    "EMBEDDED_SUPERSET": True,
}
ALERT_REPORT_SLACK_V2 = True
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
# SLACK_API_TOKEN = ""

# SQLAlchemy database connection pool settings
SQLALCHEMY_POOL_SIZE = 45  # Maximum number of connections in the pool
SQLALCHEMY_POOL_TIMEOUT = 180  # Timeout in seconds for getting a connection from the pool
SQLALCHEMY_MAX_OVERFLOW = 30  # Maximum number of connections that can be created beyond the pool size

# SQL Lab and web server timeout settings
SQLLAB_ASYNC_TIME_LIMIT_SEC = 60 * 60 * 6  # 6 hours for async SQL Lab queries
SUPERSET_WEBSERVER_TIMEOUT = 300  # 5 minutes for web server requests

# Redis settings for caching and Celery
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Redis host, default is 'redis'
REDIS_PORT = os.getenv("REDIS_PORT", "6379")  # Redis port, default is 6379
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")  # Redis database for Celery, default is 0
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")  # Redis database for query results, default is 1

# Celery configuration for task scheduling and execution
class CeleryConfig:
    # Redis broker and result backend URLs
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"

    # List of modules to import for Celery tasks
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
        "superset.tasks.llm_context",
    )

    # Celery worker settings
    worker_prefetch_multiplier = 1  # Number of tasks a worker prefetches
    task_acks_late = False  # Disable late acknowledgment of tasks

    # Task-specific annotations
    task_annotations = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",  # Limit SQL Lab query results to 100 per second
        },
    }

    # Celery beat schedule for periodic tasks
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),  # Run every minute
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),  # Run daily at 00:10
        },
        # Uncomment the following lines to enable cache warmup tasks
        # 'cache-warmup-hourly': {
        #     "task": "cache-warmup",
        #     "schedule": crontab(minute="*/30", hour="*"),  # Run every 30 minutes
        #     "kwargs": {
        #         "strategy_name": "top_n_dashboards",
        #         "top_n": 10,
        #         "since": "7 days ago",
        #     },
        # },
        "check_for_expired_llm_context": {
            "task": "check_for_expired_llm_context",
            "schedule": crontab(minute='*/5'),  # Run every 5 minutes
        },
    }

CELERY_CONFIG = CeleryConfig

# Enable dashboard embedding and allow cross-origin requests.
# Uncomment and configure CORS_OPTIONS origins for your specific use case.
ENABLE_PROXY_FIX = True
ENABLE_CORS = True
OVERRIDE_HTTP_HEADERS = {"X-Frame-Options": "ALLOWALL"}
CORS_OPTIONS = {
    "supports_credentials": True,
    # "allow_headers": ["*"],
    # "resources": ["*"],
    "origins": ["*"],  # Restrict to specific domains in production
}
TALISMAN_ENABLED = False  # Disable Talisman to avoid cookie/session issues with embedding
# Uncomment and configure Talisman for enhanced security if not using embedding:
# TALISMAN_CONFIG = {
#     "frame_options": "ALLOW_FROM",
#     "frame_options_allow_from": "",  # Specify domains allowed to embed Superset in an iframe
#     "content_security_policy": {
#         "default-src": ["'self'"],
#         "style-src": ["'self'", "'unsafe-inline'"],
#         "script-src": ["'self'", "'unsafe-inline'"],
#         "font-src": ["'self'", "data:"],
#         "img-src": ["'self'", "data:"],
#         "connect-src": ["'self'"],
#         "frame-ancestors": ["'self'"],
#     },
#     "force_https": False,
# }

# Session cookie settings to avoid conflicts with other apps on the same server
SESSION_COOKIE_NAME = "superset_session"  # Unique session cookie name

# Note: The following variables are not directly used due to a known issue.
# See: https://github.com/apache/superset/issues/11810#issuecomment-2895866554
# They are left here for reference.
# SESSION_COOKIE_HTTPONLY = True   # Prevent JavaScript access to cookies
# SESSION_COOKIE_SECURE = True     # Set to True if using HTTPS
# SESSION_COOKIE_SAMESITE = "None" # Options: 'Lax', 'Strict', or 'None' (if using Secure)

# Update Flask app session cookie settings for security.
def __mutate(app):
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,  # Set to True if using HTTPS
        SESSION_COOKIE_SAMESITE="Lax",
    )

FLASK_APP_MUTATOR = __mutate
