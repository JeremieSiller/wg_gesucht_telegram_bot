# Use the official Python 3.12 image as the base image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the poetry.lock and pyproject.toml files to the working directory
COPY poetry.lock pyproject.toml /app/

# Install Poetry
RUN pip install poetry

# Install project dependencies
RUN poetry install --no-root

# Copy the rest of the application code to the working directory
COPY . /app

# Set the entrypoint command to run the app
CMD ["poetry", "run" ,"python", "-m", "app"]
