# set the base image. Since we're running 
# a Python application a Python base image is used
FROM python:2.7
# set a key-value label for the Docker image
LABEL maintainer="Wilson Teng"
# copy files from the host to the container filesystem. 
# For example, all the files in the `techtrends` directory
# to the `/app` directory in the container
COPY ./techtrends /app
#  defines the working directory within the container
WORKDIR /app
# run commands within the container. 
# For example, invoke a pip command 
# to install dependencies defined in the requirements.txt file. 
RUN pip install -r requirements.txt
RUN python init_db.py
# expose the application port 3111
EXPOSE 3111
# provide a command to run on container start. 
# For example, start the `app.py` application.
CMD [ "python", "app.py" ]