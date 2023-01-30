FROM python:3.10
COPY . /ENGINE
WORKDIR /ENGINE
COPY ./requirments.txt requirments.txt
RUN pip install -r requirments.txt
EXPOSE 5001
ENTRYPOINT ["python"]
CMD ["main.py"]
