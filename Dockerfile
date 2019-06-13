FROM python:3.7-alpine

# Setup general environment
ENV WORK_DIR /usr/src/app
ENV SRC_DIR ${WORK_DIR}

# Configure working directory
WORKDIR ${WORK_DIR}

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools && pip install -r requirements.txt

# Add complete app
COPY ./ ${SRC_DIR}

CMD [ "python", "-m", "dooralert"]