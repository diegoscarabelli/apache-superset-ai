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

# This Dockerfile is used to build a custom Apache Superset image with additional dependencies.
# It is based on the official Apache Superset image and includes geckodriver and Firefox ESR.
ARG UPSTREAM=apachesuperset.docker.scarf.sh/apache/superset
ARG TAG=latest
FROM ${UPSTREAM}:${TAG}

# Install geckodriver with checksum verification.
ARG GECKODRIVER_VERSION=v0.36.0
ARG GECKODRIVER_CHECKSUM=0bde38707eb0a686a20c6bd50f4adcc7d60d4f73c60eb83ee9e0db8f65823e04
ARG GECKODRIVER_URL=https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz

# Labels for better metadata (following Open Container Initiative recommendations).
LABEL maintainer="Your Name <your.email@example.com>"
LABEL version="2.0"
LABEL description="Custom Apache Superset Dockerfile with additional dependencies"

# Avoid running as root; switch back to the superset user at the end.
USER root

# Combine apt-get update and install into single RUN to reduce layers and avoid cache issues.
# Includes X11/GTK libraries required for headless Firefox operation.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential default-libmysqlclient-dev wget bzip2 gnupg \
    libx11-6 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxtst6 \
    libfontconfig1 libfreetype6 libdbus-1-3 libdbus-glib-1-2 \
    libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 libcairo2 \
    libpangocairo-1.0-0 libgtk-3-0 libgbm1 libnss3 libnspr4 \
    pciutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget --no-verbose --output-document=/tmp/geckodriver.tar.gz "${GECKODRIVER_URL}" \
    && echo "${GECKODRIVER_CHECKSUM} /tmp/geckodriver.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm /tmp/geckodriver.tar.gz

# Install Firefox ESR using Mozilla's official repository.
RUN install -d -m 0755 /etc/apt/keyrings \
    && wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O /etc/apt/keyrings/packages.mozilla.org.asc \
    && echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" > /etc/apt/sources.list.d/mozilla.list \
    && echo "Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000" > /etc/apt/preferences.d/mozilla \
    && apt-get update && apt-get install -y --no-install-recommends firefox-esr \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements-local.txt and install Python packages.
COPY docker/requirements-local.txt /app/docker/requirements-local.txt
RUN uv pip install --no-cache-dir -r /app/docker/requirements-local.txt

USER superset
