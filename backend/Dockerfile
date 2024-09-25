FROM python:3.9-slim

# Upgrade pip
RUN pip install --upgrade pip

# Install requizred packages for building and running the app
RUN apt-get update && \
    apt-get install -y build-essential libasound2-dev wget && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*


# Create a non-root user for security
RUN adduser --disabled-password --gecos '' nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app

WORKDIR /home/app
USER nonroot

# Copy all the files to the container
COPY --chown=nonroot:nonroot /library /home/app/library
COPY --chown=nonroot:nonroot /backend/ /home/app/


# Setup virtual environment
ENV VIRTUAL_ENV=/home/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
RUN pip install -r requirements.txt

# Define the port number the container should expose
EXPOSE 5000

# Placeholder command
CMD ["python", "main.py"]
