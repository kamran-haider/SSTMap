#!/usr/bin/env bash
# Deploy to anaconda solvation tools channel
# conda install --yes anaconda-client
pushd .
cd $HOME/miniconda/conda-bld
FILES=*/${PACKAGENAME}*.tar.bz2
for filename in $FILES; do
    anaconda -t $CONDA_UPLOAD_TOKEN remove --force ${ORGNAME}/${PACKAGENAME}/${filename}
    anaconda -t $CONDA_UPLOAD_TOKEN upload --force -u ${ORGNAME} -p ${PACKAGENAME} ${filename}
done
popd

#anaconda upload /home/travis/miniconda3/conda-bld/linux-64/sstmap-1.1.0-py36_0.tar.bz2
