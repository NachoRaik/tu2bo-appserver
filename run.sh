#!/bin/bash
app="appserver"
docker build -t ${app} .
docker run -d -p 56733:5000 ${app} 
