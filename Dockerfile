# Define base image
FROM python:2.7
# Select working directory
WORKDIR /usr/src/app
# Copy the files in the working directory
COPY techtrends/requirements.txt /usr/src/app/ 
# Install requirements according to file
RUN pip install --no-cache-dir -r requirements.txt

COPY techtrends .
# Define the exposed port
EXPOSE 3111
# Create a database with pre-defined data 
RUN python ./init_db.py

CMD ["python","./app.py"]
