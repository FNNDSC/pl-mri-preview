FROM docker.io/fnndsc/conda:python3.10.2

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="pl-mri-preview" \
      org.opencontainers.image.description="A ChRIS plugin to preview brain volume"

# Install dependencies using conda for non-x86_64 support.
# Nibabel dependencies are installed using conda, but nibabel itself is installed
# from a custom fork on Github using pip.
RUN conda install -c conda-forge matplotlib-base=3.5.1 numpy=1.21.2 h5py=3.6.0

WORKDIR /usr/local/src/pl-mri-preview

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["mri_preview", "--help"]
