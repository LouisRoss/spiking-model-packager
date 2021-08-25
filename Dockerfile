FROM python:3

LABEL version="1.0"
LABEL description="Docker image for the Spiking Neural Network model packager."
LABEL maintainer = "Louis Ross <louis.ross@gmail.com"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY install-deps ./

RUN     echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
RUN     bash ./install-deps >>install-deps.log


COPY ["package.json", "package-lock.json", "./"]
RUN ls
#RUN npm install --production
RUN npm install
RUN npm install

#COPY . .

EXPOSE 5000

CMD ["bash"]
