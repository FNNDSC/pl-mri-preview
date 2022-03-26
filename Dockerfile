FROM docker.io/fnndsc/conda:3.10.2

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="pl-mri-preview" \
      org.opencontainers.image.description="A ChRIS plugin to preview brain volume"

# install dependencies using conda for non-x86_64 support
RUN conda install nibabel=3.2.2 matplotlib-base=3.5.1

WORKDIR /usr/local/src/pl-mri-preview

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["mri_preview", "--help"]
