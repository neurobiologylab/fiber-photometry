FROM jupyter/datascience-notebook:ubuntu-22.04
sudo apt-get install libxcb-xinerama0
RUN pip install --upgrade setuptools
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

# Configure jupyter, set up password
RUN echo "c.NotebookApp.password = u'sha1:29add7157178:365482399ea9df01949adbbfb5807d84261926b2'" >> ~/.jupyter/jupyter_notebook_config.py
USER root
CMD ["bash", "-c", "jupyter notebook --notebook-dir=/workspace --ip 0.0.0.0 --no-browser --allow-root"]

