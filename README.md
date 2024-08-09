# Babel Fish
<p align="center">
  <img src="https://github.com/user-attachments/assets/018a847e-2ccc-4f78-9e92-29dcc05f799e" alt="babel fish">
</p>

## Purpose

To assist in the live translation between different languages.


## Demo
Initial proof of concept
https://github.com/user-attachments/assets/a96efc79-0f02-4c79-bcf2-c1e3a2bfcffd


## Design Goals
- start with solving the problem in the simplest way
- adjust the solution to be cloud service agnostic
- adjust the solution to be scalable microservices

## Design

Design Option: Distributed Workers
Pros:
- horizontal scalability at the API and worker level
- asynchronous processing of tasks

<p align="center"> 
  <img src="https://github.com/user-attachments/assets/07deffdb-5e8c-4699-a609-112cf122da3e">
</p>
