FROM python:3.10-slim

# Allow insecure repositories (workaround for GPG error)
RUN echo 'Acquire::AllowInsecureRepositories "true";' > /etc/apt/apt.conf.d/99insecure \
    && echo 'Acquire::AllowDowngradeToInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99insecure

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        firefox-esr \
        xvfb \
        xauth \
        wget \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        libdbus-glib-1-2 \
        libxt6 \
        libxss1 \
        libnss3 \
        libxcomposite1 \
        libxrandr2 \
        libgbm1 \
        libxdamage1 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libatspi2.0-0 \
        && rm -rf /var/lib/apt/lists/*

# Install geckodriver
ENV GECKODRIVER_VERSION v0.34.0
RUN wget --no-verbose https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -xzf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app
WORKDIR /app

# Run Xvfb and your main.py
CMD ["xvfb-run", "-a", "python", "src/main.py"] 