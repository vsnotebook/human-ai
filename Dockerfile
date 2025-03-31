# Python image to use.
FROM python:3.12-alpine

# Set the working directory to /app
WORKDIR /app

# Set production environment
ENV APP_ENV=prod
#ENV PYTHONPATH=/app

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run app with module mode when the container launches
#ENTRYPOINT ["python", "-m", "src.main-web", "--env", "production"]
ENTRYPOINT ["python", "-m", "src.main_web"]
