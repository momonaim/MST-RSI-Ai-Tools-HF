## Use the official Python 3.9 image
FROM python:3.9

## set the working directory to /code
WORKDIR /code

## Copy the current directory contents in the container at /code
COPY ./requirements.txt /code/requirements.txt

## Install the requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Set up a new user named "user" 
RUN useradd user
# Switch to the "user" user
USER user

# Set home to the user's home directory

ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

# Run the Flask application
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:app"]
#CMD ["python", "app:app"]
