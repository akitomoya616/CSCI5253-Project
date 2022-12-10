# CSCI 5253 Project

## Sitong Lu

## Project Overview
A shopping history collector that take shopping receipt from user, receive command and result the corresponding result back to user.

Proposal can be found in [Project Proposal](documents/proposal/Project%20Proposal.pdf).

Project write-up can be found in [Project Written Report](documents/report/CSCI5253-Final-Project-Write-Up.pdf).

Project presentation slide can be found in [Project Report Slide](documents/report/CSCI5253-Final-Presentation.pptx).

Recorded project presentation together with the live demo can be found on [Youtube](https://youtu.be/wo2yj7iWooI).

## Installation Instruction
To get the project up and running, please follow the instructions in the README files for [redis](redis/README.md), [rest](rest/README.md), and [sql](redis/README.md) for some extra setup installation.

To add more logs in any program, please reference [log's README](logs/README.md) and check its current application approach in [worker.py](worker/worker.py).

## Deployment
All the necessary deployment command has been written in [deploy-all script for GKE](deploy-all.sh) and [deploy-all script for local environment](deploy-local-dev.sh). You can also use [this deployment deletion script](delete-all.sh) to delete all the deployment at once. To run it on GKE, please type `chmod 777 deploy-all.sh` in the terminal first in order to allow Google Cloud accept script and then run `./deploy-all.sh` in the root directory.